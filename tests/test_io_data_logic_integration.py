import json
from pathlib import Path

import pytest

import data_manager
from io_manager import IOManager
from logic_manager import LogicManager


@pytest.mark.parametrize(
    ("answer", "expected_status"),
    [("yes", "closed"), ("no", "active")],
    ids=["confirm-closes-report", "decline-keeps-report-active"],
)
def test_report_match_confirmation_across_layers(
    tmp_path, monkeypatch, answer, expected_status, capsys
):
    monkeypatch.setattr(data_manager, "DATA_FILE", tmp_path / "reports.json")
    monkeypatch.setattr(data_manager, "IMAGE_DIRECTORY", tmp_path / "images")
    monkeypatch.setattr(data_manager, "TEMP_DIRECTORY", tmp_path / "temp")
    data = data_manager.DataManager()

    report = data.save_new_reports({
        "report_type": "found",
        "category": "bottle",
        "date": "25-09-2026",
    })
    assert report is not None
    candidate, = data.get_reports_by_category("bottle")

    # Use a recorded analysis in place of a live AI result.
    fixture_path = Path(__file__).resolve().parents[1] / "logic_test_data" / "success.json"
    fixture_report = json.loads(fixture_path.read_text(encoding="utf-8"))[0]
    candidate["similarity_analysis"] = fixture_report["similarity_analysis"]

    match = LogicManager().get_best_match([candidate], "24-09-2026")
    assert match is not None
    assert match["report"]["case_id"] == report["case_id"]
    assert match["evaluation"]["status"] == "RECOMMENDED_MATCH"

    confirmed = IOManager().resolve_best_match(
        match,
        input_function=lambda prompt: answer,
    )
    assert confirmed is (answer == "yes")

    if confirmed:
        assert data.update_report_status(match["report"]["case_id"], "closed")

    saved, = data_manager.DataManager().load_reports()
    assert saved["status"] == expected_status
    assert "similarity_analysis" not in saved
    capsys.readouterr()
