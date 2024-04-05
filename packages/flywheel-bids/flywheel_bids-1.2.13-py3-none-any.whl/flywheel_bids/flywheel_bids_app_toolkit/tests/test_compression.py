import datetime
import fnmatch
import shutil
from pathlib import Path
from zipfile import ZipFile

import pytest

from flywheel_bids.flywheel_bids_app_toolkit.compression import (
    prepend_index_filename,
    unzip_archive_files,
    walk_tree_to_exclude,
    zip_htmls,
    zip_html_and_svg_files,
)
from flywheel_bids.flywheel_bids_app_toolkit.utils.helpers import make_dirs_and_files


def test_walk_tree_to_exclude(tmp_path):
    files = [
        Path("bids/gear/analysis/out.txt"),
        Path("bids/gear/analysis/chart.md"),
        Path("bids/gear/analysis/final.nii"),
        Path("bids/gear/analysis/buried/result.nii.gz"),
    ]
    paths = [str(tmp_path / file) for file in files]
    make_dirs_and_files(paths)
    root_dir = Path(tmp_path)

    # Test case 1: Excluding files that match patterns in the inclusion list
    inclusion_list = ["*.txt", "*.md"]
    excluded_items = walk_tree_to_exclude(root_dir, inclusion_list)
    for item in excluded_items:
        assert any(fnmatch.fnmatch(item, pattern) for pattern in inclusion_list) is False

    # Test case 2: Including files that do not match any pattern in the inclusion list
    inclusion_list = ["*.txt", "*.md"]
    excluded_items = walk_tree_to_exclude(root_dir, inclusion_list)
    for item in excluded_items:
        assert not any(fnmatch.fnmatch(item, pattern) for pattern in inclusion_list)

    # Test case 3: Empty inclusion list
    inclusion_list = []
    excluded_items = walk_tree_to_exclude(root_dir, inclusion_list)
    assert all(i in excluded_items for i in paths)


def test_prepend_index_filename(tmp_path):
    test_file = tmp_path / "test_ix_file.txt"
    test_file.touch()

    updated_filename = prepend_index_filename(test_file)

    # Assert the expected result
    expected_filename = f"{tmp_path}/{datetime.datetime.now().strftime('%Y-%m-%d_%H')}_test_ix_file.txt"
    assert str(updated_filename) == expected_filename


@pytest.fixture
def test_archive(tmp_path):
    # Create a temporary test directory
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Create a test zip file
    test_zip_path = test_dir / "test_archive.zip"
    with ZipFile(test_zip_path, "w") as zipf:
        zipf.writestr("file_1.txt", "Test file 1")
        zipf.writestr("file_2.txt", "Test file 2")

    yield test_dir, test_zip_path

    # Clean up after the test
    shutil.rmtree(test_dir)


def test_unzip_archive_files(test_archive, mock_context):
    test_dir, test_zip_path = test_archive
    mock_context.get_input_path.side_effect = lambda key: {"archive_key": Path(test_zip_path)}.get(key)

    result_dir = unzip_archive_files(mock_context, "archive_key")

    # Assert that the extracted files exist in the result directory
    assert (Path(result_dir) / "file_1.txt").is_file()
    assert (Path(result_dir) / "file_2.txt").is_file()

    # Assert that the archive key in app_options has been updated to the extracted directory
    expected_result_dir = test_dir / "test_archive"
    assert result_dir == expected_result_dir

    @pytest.fixture
    def test_htmls(tmp_path):
        # Create a temporary test directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Create test HTML files
        html_file1 = test_dir / "file_1.html"
        html_file1.touch()

        html_file2 = test_dir / "folder" / "file_2.html"
        html_file2.parent.mkdir()
        html_file2.touch()

        yield test_dir, html_file1, html_file2

        # Clean up
        shutil.rmtree(test_dir)

    # This test ends up testing the sub-methods, too...
    def test_zip_htmls(test_htmls, tmp_path):
        test_dir, html_file1, html_file2 = test_htmls

        output_dir = tmp_path
        destination_id = "test_destination_id"
        html_path = str(test_dir)

        zip_htmls(output_dir, destination_id, html_path)

        # Assert that the zip files are created in the output directory
        zip_index_file = tmp_path / f"{destination_id}_{Path(html_file1).name}.zip"
        assert zip_index_file.is_file()
