import logging
from os.path import commonpath
from pathlib import Path
from typing import List, Union

log = logging.getLogger(__name__)


def check_bids_dir(app_context):
    """Check if the archived input unzipped with dataset description at the top level.

    Sets the BIDS directory to the top-level directory, where the
    dataset_description.json is located. Particularly useful for group-level zipped
    analyses.

    Note to FW devs: This method came out of a test case failure. Using an input archive from either the project-level or subject-level introduces another directory under /flywheel/v0/bids, resulting in gear failure. This method quickly adapts to a (accidental) nested structure.

    Args:
        app_context (BIDSAppContext): Details about the gear setup and BIDS options
    """
    dd_loc = list(Path(app_context.bids_dir).rglob("dataset_description.json"))[0]
    app_context.bids_dir = dd_loc.parent


def create_analysis_output_dir(app_context):
    """
    Create analysis directory with the unique destination identifier.
    Args:
        app_context (BIDSAppContext): Details about the gear setup and BIDS options
    """
    # Create output directory
    log.info("Creating output directory %s", app_context.analysis_output_dir)
    Path(app_context.analysis_output_dir).mkdir(parents=True, exist_ok=True)


def determine_dir_structure(search_dir):
    """
    The directory structure during any given BIDS App analysis is somewhat obscure.
    If the file path in the code is incorrect, this method can be called to
    help build the debugging message.

    Note: Example use in fw_gear_bids_mriqc.utils.store_iqms._find_output_files
    """
    search_path = Path(search_dir)
    for file_path in search_path.glob("**/*"):
        if file_path.is_file():
            log.debug(file_path)


def find_BIDS_algo_results_dir(destination_id: str, output_dir: Union[Path, str]) -> Path:
    top_level = Path(output_dir).parent
    analysis_dirs = list(top_level.rglob(f"**/*{destination_id}*"))
    if len(analysis_dirs) > 1:
        common_path = commonpath(analysis_dirs)
        return Path(common_path)
    elif not analysis_dirs:
        raise ValueError(f"Did not find a folder matching {destination_id}")
    else:
        return analysis_dirs[0]


def make_dirs_and_files(files: Union[List[str], List[Path]]) -> None:
    """Create directories and touch files.

    Note: fw_gear_{BIDS_app}.utils.ry_run.py will use this method,
    but it is common enough to be part of a toolkit. One may also
    use it for testing setup.

    Args:
        files: paths to files to be created
    """
    for ff in files:
        if Path(ff).exists():
            log.debug("Exists: %s", str(ff))
        else:
            log.debug("Creating: %s", str(ff))
            dir_name = Path(ff).parents[0]
            Path(dir_name).mkdir(parents=True, exist_ok=True)
            Path(ff).touch(mode=0o777, exist_ok=True)


def split_extension(filename: str):
    """Remove flexible number of extensions.

    Imaging files and archives tend to have flexible numbers of extensions.
    This simple method deals with all extensions to return the most basic
    basename. e.g., /path/to/my/output/archive.tar.gz returns 'archive'

    Note: don't extend this method to all filenames, since 1.2.34.567.nii.gz
    or another UID-esque name would return problematically.
    :param filename (str): any filename with or without multiple extensions
    :return filename (str) Non-UID basename without any extensions
    :return ext (str) The combined suffixes from the original filename
    """
    ext = "." + ".".join(Path(filename).name.split(".")[1:])
    filename = str(Path(filename).stem.split(".")[0])
    if len(filename) < 4:
        log.warning(f"Is {filename} the correct filename without an extension?")
    return filename, ext
