from typing import Dict, List, Tuple

from flywheel_gear_toolkit import GearToolkitContext
from flywheel_gear_toolkit.utils.file import sanitize_filename

from . import BIDSAppContext
from .utils.query_flywheel import (
    get_analysis_run_level_and_hierarchy,
    orchestrate_download_bids,
)


def get_bids_data(
    gear_context: GearToolkitContext,
    bids_modalities: List[str],
    tree_title: str,
    skip_download: bool = False,
    tree=True,
) -> Tuple[Dict, List[str]]:
    """Get the data in BIDS structure.

    Get the data in BIDS structure and return the subject_label and
    run_label corresponding to the destination container.
    It also returns any error found downloading the BIDS data.

    For FW gears, it downloads the data
    For RL containers, it just points/links to the storage folder
    It should be independent of the specific BIDS-App

    Args:
        gear_context (GearToolkitContext): gear context
        bids_modalities (List): BIDS modality folders to check for download
        tree_title (str): title for the BIDS tree
        skip_download (bool): Should the data be downloaded?
        tree (bool): Create HTML file that shows BIDS "Tree" like output?
    Returns:
        subject_label (str): FW subject_label, (from the hierarchy of the destination
            container)
        run_label (str): FW run_label, (from the hierarchy of the destination container)
        errors (list[str]): list of generated errors
    """
    errors = []

    # Given the destination container, figure out if running at the project,
    # subject, or session level.
    hierarchy = get_analysis_run_level_and_hierarchy(gear_context.client, gear_context.destination["id"])

    # This is the label of the project, subject or session and is used
    # as part of the name of the output files.
    run_label = hierarchy["run_label"]
    run_label = sanitize_filename(run_label)

    error_code = orchestrate_download_bids(
        gear_context,
        hierarchy,
        tree=tree,
        tree_title=tree_title,
        src_data=False,
        folders=bids_modalities,
        skip_download=skip_download,
    )

    if error_code > 0:
        errors.append("BIDS Error(s) detected")

    return (
        {
            "subject_label": hierarchy.get("subject_label", None),
            "session_label": hierarchy.get("session_label", None),
            "run_label": run_label,
        },
        errors,
    )


def set_participant_info_for_command(app_context: BIDSAppContext, participant_info: Dict) -> BIDSAppContext:
    """Define the participant label for the official BIDS App command.

    For BIDS Apps that run at the participant level, set the
     "participant_label" from the container from which it was launched.
    Args:
        app_context:
        participant_info (Dict): subject_label, session_label, and run_label
    """
    for k, v in participant_info.items():
        # In general, BIDS-Apps take only the (subject) label, without the "sub-" part:
        if v:
            if v.startswith("sub-"):
                v = v[len("sub-") :]

            setattr(app_context, k, v)
