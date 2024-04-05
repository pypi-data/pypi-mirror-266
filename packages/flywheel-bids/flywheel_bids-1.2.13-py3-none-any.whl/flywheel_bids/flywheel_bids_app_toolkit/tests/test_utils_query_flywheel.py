import json
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from importlib_resources import files

from flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel import (
    copy_bidsignore_file,
    get_fw_details,
)

BIDS_PATH = files("tests.assets").joinpath("dataset")


@pytest.mark.parametrize(
    "bidsignore_condition, copied_file",
    [("use", ".bidsignore"), ("skip", "found.bidsignore")],
)
def test_copy_bidsignore_file(bidsignore_condition, copied_file, tmp_path):
    # Set up dummy file
    input_dir = Path(tmp_path) / "input"
    input_dir.mkdir(parents=True)
    bidsignore = None
    if bidsignore_condition == "use":
        bidsignore = input_dir / copied_file
        bidsignore.touch()
    else:
        tmp_file = input_dir / copied_file
        tmp_file.touch()

    copy_bidsignore_file(BIDS_PATH, input_dir, bidsignore)
    expected_result = Path(BIDS_PATH) / ".bidsignore"

    assert expected_result.exists()

    # Clean-up
    os.remove(expected_result)


def test_get_fw_details(extended_gear_context):
    extended_gear_context.manifest.get.side_effect = lambda key: {
        "custom": {"gear-builder": {"image": "flywheel/bids-qsiprep:0.0.1_0.15.1"}}
    }.get(key)
    extended_gear_context.client.get.side_effect = MagicMock()
    destination, gear_builder_info, container = get_fw_details(extended_gear_context)
    assert isinstance(destination, MagicMock)
    assert isinstance(gear_builder_info, dict)
    assert isinstance(container, str)
