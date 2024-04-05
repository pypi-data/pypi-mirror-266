"""Tools to help zip, unzip, and process HTML, result, or archived files."""
import datetime
import fnmatch
import logging
import os
import re
from pathlib import Path
from typing import List, Union
from zipfile import ZipFile

from bs4 import BeautifulSoup
from flywheel_gear_toolkit import GearToolkitContext
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive, zip_output

from .utils.helpers import split_extension

log = logging.getLogger(__name__)


def walk_tree_to_exclude(root_dir: Path, inclusion_list: List):
    """
    Walks a tree and excludes files or directories not specified in the inclusion list.
    Returns a list of excluded files and folders.

    GTK requires an exclusionary list for `zip_output`. Thus, this method
    combs the tree and reports which files to pass to `zip_output` for exclusion.

    Args:
        root_dir (Path): directory to walk to locate files to exclude
        inclusion_list (List): Files to keep for zipping. If a file is
        encountered during the walk and not in this list, it will be returned
        as one of the files to exclude, when GTK zips the contents of the root_dir.
    """
    excluded_items = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter and process the filenames
        for filename in filenames:
            if not any(fnmatch.fnmatch(filename, pattern) for pattern in inclusion_list):
                file_path = os.path.join(dirpath, filename)
                excluded_items.append(file_path)

    return excluded_items


def prepend_index_filename(orig_filename: Union[Path, str]):
    """
    Add the analysis date and time to the beginning of the filename.

    Sometimes, there is an index.html file in the analysis' output.
     This file will be need to be identified, temporarily renamed,
     and then restored to the original location. (Other htmls are
     temporarily named "index.html" prior to being zipped, so this
     method helps avoid files being overwritten.)
    :param orig_filename: full path to the file that needs to be
            temporarily renamed.
    :return
        updated_filename: new location/name of the file, so that the file
        can be returned to its original location after the other results are
        marked and zipped.
    """
    now = datetime.datetime.now()
    updated_filename = Path(
        Path(orig_filename).parents[0],
        now.strftime("%Y-%m-%d_%H") + "_" + Path(orig_filename).name,
    )
    os.rename(orig_filename, updated_filename)
    return updated_filename


def unzip_archive_files(gear_context: GearToolkitContext, archive_key: str, unzip_dir: Path = None):
    """Unzip archived files (e.g., FreeSurfer) from previous runs.

    This method is called when the BIDSAppContext object is instantiated.

    Args:
        gear_context (GearToolkitContext): Details about the gear run
        archive_key (str): Key to retrieve/set from app_options
        unzip_dir (Path): target destination path for the unzipped archive
    Returns:
        unzip_dir (Path): newly unzipped directory
    """
    zipped_dir = gear_context.get_input_path(archive_key)
    # Keep all the unzipping in /flywheel/v0/work or output, if possible,
    # to be compatible with HPC
    if not unzip_dir:
        unzip_dir = Path(zipped_dir).with_suffix("")

    # Ensure that the destination exists
    Path(unzip_dir).mkdir(parents=True, exist_ok=True)

    unzip_archive(str(zipped_dir), str(unzip_dir))

    # Sanity check
    if unzip_dir.is_dir():
        log.debug(f"Unzipped archive to {unzip_dir}")

    return unzip_dir


def zip_derivatives(app_context, alt_derivatives: List[str] = None):
    """
    Zip any and all derivative folders created by the BIDS App.

    Args:
        app_context (BIDSAppContext): Details about the gear setup and BIDS options
        alt_derivatives (List): Optional; any other directories to look through for
            compression. e.g., qsirecon in addition to qsiprep
    """
    derivatives = [app_context.bids_app_binary]
    # In case there are other derivative directories to consider,
    # add them to the list. (Not all apps will have multiple dirs
    # to search)
    if alt_derivatives is not None:
        derivatives.extend(alt_derivatives)

    for derivative in derivatives:
        derivative_dir = Path(app_context.analysis_output_dir) / derivative

        if derivative_dir.exists():
            zip_file_name = (
                app_context.output_dir / f"{app_context.bids_app_binary}_{app_context.destination_id}_{derivative}.zip"
            )
            zip_output(
                str(app_context.analysis_output_dir),
                derivative,
                str(zip_file_name),
                dry_run=False,
                exclude_files=None,
            )
            zip_htmls(
                app_context.output_dir,
                app_context.destination_id,
                derivative_dir,
            )


def zip_htmls(output_dir: Union[Path, str], destination_id: str, results_dir: Union[Path, str]):
    """Zip all .html files at the given path, so they can be displayed
    on the Flywheel platform.

    Each html file must be added to the main HTML zip archive, which
    is being called index.html.
    Somehow, renaming supporting files index.html and overwriting the
    index.html.zip with the newly renamed index.html via zip_it_zip_it_good
    makes the full HTML report available to the Flywheel platform.

    Args:
        output_dir (Path): Location for the zip to end up.
        destination_id (str): Flywheel ID
        results_dir (Path): Location to search for htmls to zip.
    """
    log.info("Creating viewable archives for all html files")

    if Path(results_dir).exists():
        unzipped_htmls = search_for_html_report_files(results_dir)
        if unzipped_htmls:
            for html in unzipped_htmls:
                try:
                    zip_html_and_svg_files(results_dir, html, destination_id, output_dir)
                except Exception as e:
                    log.error(
                        f"Unable to zip {html.name} properly.\n" f"Continuing with gear clean-up. \n" f"Error: {e}"
                    )
        else:
            log.warning("No *.html files at " + str(results_dir))
    else:
        log.error("Path NOT found: " + str(results_dir))


def search_for_html_report_files(folder_path: Path):
    html_files = list(Path(folder_path).rglob("*.html"))
    return html_files


def parse_BIDS_suffix(file_name: Union[Path, str]):
    """Find the modality/suffix.

    e.g., T1w, bold
    """
    root, ext = split_extension(file_name)
    try:
        return root[root.rindex("_") :]
    except ValueError:
        return None


def zip_html_and_svg_files(results_dir, results_html_filename: Path, destination_id, output_dir):
    """
    Find all related results files, update relative links, and zip.

    :param results_dir: wherever the unzipped results live;
            probably app_context.analysis_output_dir
    :param results_html_filename (Path): PosixPath; access just the base name describing the
            zipped result; e.g., sub-TOME3024_ses-Session2_acq-MPRHA_T1w.html with results_html_filename.name
    :param destination_id: Unique identifier for the analysis
    :param output_dir: /flywheel/v0/output for all intents and purposes
    :return:
    """
    zip_name = destination_id + "_" + str(results_html_filename.name) + ".zip"
    archive_name = str(Path(output_dir).joinpath(Path(zip_name)))
    # Instantiate the zip_file object, which will have
    # the results_html_filename
    zip_file = ZipFile(archive_name, "w")

    # Is there a time when there will not be an underscore to differentiate the
    # modality? Should we handle a "super subject" html?
    bids_suffix = parse_BIDS_suffix(results_html_filename.name)

    if not results_html_filename.is_file():
        results_html_filename = Path(results_dir) / Path(results_html_filename.name)
        if not results_html_filename.is_file():
            log.error("Location of the results html specified incorrectly.")

    # Read the original HTML
    with open(results_html_filename, "r") as f:
        contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")
    # Find the links
    img_tags = soup.find_all("img")
    if img_tags:
        orig_img_tags = [it["src"] for it in img_tags]
        for img_tag in img_tags:
            svg_name = img_tag.get("src", "")
            log.debug(f"svg_name: {svg_name}")

            # Find summary htmls
            pattern = r"^sub-.*\.html*"
            regex = re.compile(pattern)

            # Filter the SVG files for the ones that match the
            # modality/suffix being reported and zipped
            if svg_name and (bids_suffix and bids_suffix in svg_name) or (regex.match(str(results_html_filename.name))):
                svg_path = Path(results_dir) / svg_name
                # log.debug(f"svg_path: {svg_path}")
                # Send to the archive
                zip_file.write(svg_path, svg_path.name)
                # Update the relative link in the original (still
                # unzipped) HTML with the new location of the svg
                img_tag["src"] = archive_name[:-4] + "/" + svg_path.name
        log.debug(f"Updating img_tags: {[it['src'] for it in img_tags if it not in orig_img_tags]}")
        # Write the updated HTML back to the file
        with open(results_html_filename, "w") as f:
            f.write(str(soup))
    # Zip the archive with the actual, file path-modified
    # html renamed to "index.html" for Flywheel platform
    # to display properly
    zip_file.write(results_html_filename, "index.html")
