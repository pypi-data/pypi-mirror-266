import logging

from . import classifications, templates, utils
from .project_tree import TreeNode

logger = logging.getLogger("curate-bids")


def determine_enum(theproperty, key, classification):
    """

    obj:  {'Task': '', 'Run': '', 'Filename': '', 'Acq': '', 'Rec': '', 'Path': '', 'Folder': 'func', 'Echo': ''}
    property: {'default': 'bold', 'enum': ['bold', 'sbref', 'stim', 'physio'], 'type': 'string', 'label': 'Modality Label'}
    classification:  {u'Intent': u'Functional'}

    """
    # Use the default value
    enum_value = theproperty.get("default", "")
    # If the default value is '', try and determine if from 'enum' list
    if not enum_value:
        # If key is modality, iterate over classifications dict
        if key == "Modality":
            for data_type in classifications.classifications.keys():
                # Loops through the enum values in the propdef, allows for prioritization
                for enum_value in theproperty.get("enum", []):
                    enum_req = classifications.classifications[data_type].get(enum_value)
                    if enum_req and utils.dict_match(enum_req, classification):
                        return enum_value

    return enum_value


# add_properties(properties, obj, measurements)
# Populates obj with properties defined in a namespace template
# Adds each key in the properties list and sets the value to the value specified in 'default' attribute
# Properties may be of type string or object. Will add other types later.
# Measurements passed through function so that Modality value can be determined


def add_properties(properties, obj, classification):
    for key in properties:
        proptype = properties[key]["type"]
        if proptype == "string":
            # If 'enum' in properties, seek to determine the value from enum list
            if "enum" in properties[key]:
                obj[key] = determine_enum(properties[key], key, classification)
            elif "default" in properties[key]:
                obj[key] = properties[key]["default"]
            else:
                obj[key] = "default"
        elif proptype == "object":
            obj[key] = properties[key].get("default", {})
        elif "default" in properties[key]:
            obj[key] = properties[key]["default"]
    return obj


def update_properties(properties, context, obj):
    """Updates object values for items in properties list containing an 'auto_update' attribute.

    This is done ony after the properties have been initialized using the context so values from the
    BIDS namespace can be used.

    The basic 'auto_update' is specified using a string type containing tags to be replaced from values
    in the 'context' object.  If 'auto_update' is a dictionary, '$process', '$value' and '$format' can be
    used to do more complicated things.

    If 'auto_update' is an 'object' type, the properties therein are processed recursively.

    :param properties: (dict) Properties of the template to be updated.
    :param context: (dict) the current container or file where property values can be found.
    :param obj: (dict) the result being updated.
    :return: obj
    """

    for key in properties:
        proptype = properties[key]["type"]
        if proptype == "string":
            if "auto_update" in properties[key]:
                auto_update = properties[key]["auto_update"]
                if isinstance(auto_update, dict):
                    if auto_update.get("$process"):
                        value = utils.process_string_template(auto_update["$value"], context)
                    else:
                        value = utils.dict_lookup(context, auto_update["$value"])
                    obj[key] = utils.format_value(auto_update["$format"], value)
                else:
                    obj[key] = utils.process_string_template(auto_update, context)

                logger.debug(f"Setting <{key}> to <{obj[key]}>")
        elif proptype == "array":
            pass  # so far, no need to auto_update any arrays
        elif proptype == "object":
            obj[key] = update_properties(properties[key]["properties"], context, {})
        else:
            logger.error("Unsupported property type <{proptype}>")

    return obj


# process_matching_templates(context, template)
# Accepts a context object that represents a Flywheel container and related parent containers
# and looks for matching templates in namespace.
# Matching templates define rules for adding objects to the container's info object if they don't already exist
# Matching templates with 'auto_update' rules will update existing info object values each time it is run.


def process_matching_templates(context: TreeNode, template: templates.Template, upload=False):
    """
    Upload or update container following BIDS rules from a template JSON.

    Identify whether the container already exists. If not, try to match
    (1) upload_rules, if they exist, (2) rules from the template. Reports
    back if the template is non-existent or rules are not available for the
    container.
    If the container exists, attempt to update info.{BIDS} section of metadata

    :param TreeNode context: dictionary of the container with the original, Flywheel info blob
    :param template: information from the selected or provided template JSON file
    :param bool upload: Put image onto FW instance.
    :return container: Flywheel container with info fields defined per designated template + rules
    """
    # Default values
    namespace = template.namespace

    container_type = context["container_type"]
    container = context[container_type]

    if container.get("info", {}).get(namespace) == "NA":
        logger.debug(f"info.{namespace} is NA")
        return container

    if context["container_type"] == "file":
        label = container.get("name", "")
    else:
        label = container.get("label", "")

    templateDef = None

    # Is this the first time that the images are being uploaded?
    find_rule_match = (
        ("info" not in container)
        or (namespace not in container["info"])
        or ("template" not in container["info"][namespace])
    )

    # add objects based on template if they don't already exist
    if find_rule_match:
        logger.debug(
            f"'info' not in container OR "
            f"{namespace} not in 'info' OR "
            f"'container template' not in info.{namespace}.  "
            f"Performing rule matching\n\n"
        )

        # Do initial rule matching
        rules = template.rules
        # If matching on upload, test against upload_rules as well
        # The upload_rule may be as simple as {'container_type': 'file', 'parent_container_type': 'acquisition'}
        if upload:
            logger.debug("Matching on upload, testing against upload_rules\n")
            rules = rules + template.upload_rules

        # TODO: Prioritize the rules with modality type that matches label
        for rule in rules:
            logger.debug(f"checking rule: <{rule.id}> for container template: <{rule.template}>\n")
            if rule_matches(rule, context, label):
                templateDef = template.definitions.get(rule.template)
                if templateDef is None:
                    raise Exception("Unknown container template: {0}".format(rule.template))
                else:
                    match_info = create_match_info_update(
                        rule, context, container, templateDef["properties"], namespace
                    )
                    # Processing of the template JSON is explained in templates.apply_initializers
                    rule.initializeProperties(match_info, context)
                    if rule.id:
                        template.apply_custom_initialization(rule.id, match_info, context)
                        find_rule_match = False
                break

    if not find_rule_match:
        # Do auto_updates
        if not templateDef:
            templateDef = template.definitions.get(container["info"][template.namespace]["template"])

        if templateDef:
            data = update_properties(templateDef["properties"], context, {})
            container["info"][namespace].update(data)

    return container


def rule_matches(rule: templates.Rule, context: TreeNode, label: str):
    """
    :param rule: Template rule being examined
    :param context (TreeNode): dictionary of the container with the original, Flywheel info blob
    :param label (str): container name or label, depending on Flywheel hierarchy level
    :return: match_status (Boolean)
    """
    if rule.test(context):
        logger.debug(f"Matches rule called {rule.id}\n")
        if rule.id:
            logger.info(f"{label} matches container template {rule.template} {rule.id}\n")
        else:
            logger.info(f"{label} matches container template {rule.template} \n")
        return True
    else:
        logger.debug(f"rule {rule.conditions} not matched for {label} in " f"{context['parent_container_type']}\n")
        return False


def create_match_info_update(rule, context, container, template_properties, namespace):
    """Prepare dictionary for metadata update related to BIDS curation per the specific rule."""
    if "info" not in container:
        container["info"] = {}

    match_info = container["info"].get(namespace, {})
    match_info["template"] = rule.template
    match_info["rule_id"] = rule.id
    container["info"][namespace] = add_properties(template_properties, match_info, container.get("classification"))
    if context["container_type"] in ["session", "acquisition", "file"]:
        match_info["ignore"] = False
    return match_info


def process_resolvers(context: TreeNode, template: templates.Template):
    """
    Perform second stage path resolution based on template rules

    Args:
        session (TreeNode): The session node to search within
        context (dict): The context to perform path resolution on (dictionary of the container with the original, Flywheel info blob)
        template (Template): The template
    """
    namespace = template.namespace

    container_type = context["container_type"]
    container = context[container_type]

    if (
        ("info" not in container)
        or (namespace not in container["info"])
        or ("template" not in container["info"][namespace])
    ):
        return

    # Determine the applied template name
    template_name = container["info"][namespace]["template"]
    # Get a list of resolvers that apply to this template
    resolvers = template.resolver_map.get(template_name, [])

    # Apply each resolver
    for resolver in resolvers:
        resolver.resolve(context)
