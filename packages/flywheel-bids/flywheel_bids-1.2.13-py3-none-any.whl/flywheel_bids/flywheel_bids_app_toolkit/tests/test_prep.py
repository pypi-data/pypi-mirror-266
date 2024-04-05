from flywheel_bids.flywheel_bids_app_toolkit.prep import set_participant_info_for_command


def test_set_participant_info_for_command(mock_app_context):
    participant_info = {
        "subject_label": "sub-01",
        "session_label": "ses-01",
        "run_label": "run-01",
        "valueless_key": None,
    }

    set_participant_info_for_command(mock_app_context, participant_info)

    assert mock_app_context.subject_label == "01"
    assert mock_app_context.session_label == "ses-01"
    assert mock_app_context.run_label == "run-01"
    assert not hasattr(mock_app_context, "valueless_key")
