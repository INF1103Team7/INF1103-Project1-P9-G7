
import json
from pathlib import Path

import pytest

from logic_manager import LogicManager
from logic_classes.threshold_config import ThresholdConfig


TEST_FOLDER = Path(__file__).parent.parent / "logic_test_data"

LOST_REPORT_DATE = "20-09-2026"


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def threshold_config():
    return ThresholdConfig()


@pytest.fixture
def logic_manager(threshold_config):
    return LogicManager(threshold_config=threshold_config)


def load_test_data(filename):
    file_path = TEST_FOLDER / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

@pytest.fixture(scope="module")
def best_match_summary():
    lines = []
    yield lines

    if lines:
        print("\n=== Best match summary ===")
        for line in lines:
            print(line)
# ============================================================
# HELPER FUNCTIONS
# ============================================================

def assert_evaluation_structure(evaluation):
    """Check that an evaluation contains the expected fields."""

    assert isinstance(evaluation, dict)

    assert "status" in evaluation
    assert "final_composite_score" in evaluation
    assert "triggered_rules_list" in evaluation

    assert "matched_rules_list" in evaluation
    assert "mismatched_rules_list" in evaluation
    assert "evaluation_summary" in evaluation

# ============================================================
# 1. INDIVIDUAL JSON EVALUATIONS AND BEST MATCH
# ============================================================
def report_label(report_number, report):
    case_id = report.get("case_id") if isinstance(report, dict) else None
    if case_id:
        return f"Report {report_number} ({case_id})"
    return f"Report {report_number}"


@pytest.mark.parametrize("filename", [
    "success.json",
    "strong_match.json",
    "weak_match.json",
    "multi_rule.json",
    "wrong_format.json",
    "missing_keys.json",
    "tie_score.json",
])
def test_evaluate_analysis(logic_manager, filename, best_match_summary):
    ai_result_list = load_test_data(filename)
    assert isinstance(ai_result_list, list)

    best_match = logic_manager.get_best_match(
        ai_result_list,
        lost_report_date=LOST_REPORT_DATE,
    )

    if best_match is None:
        summary_line = f"{filename} | Best match: none"
    else:
        winner = best_match["report"]
        winner_number = ai_result_list.index(winner) + 1
        evaluation = best_match["evaluation"]
        assert_evaluation_structure(evaluation)

        score = evaluation["final_composite_score"]
        score_text = f"{score:g}/100" if score is not None else "N/A"

        summary_line = (
            f"{filename} | Best match: {report_label(winner_number, winner)}"
            f" | {evaluation['status']} | {score_text}"
        )

    best_match_summary.append(summary_line)
    print(f"\n{summary_line}")
    for report_number, report in enumerate(ai_result_list, start=1):
        evaluation = logic_manager.matcher.evaluate_analysis(
            report,
            LOST_REPORT_DATE,
        )

        print(f"  {report_label(report_number, report)}")
        evaluation_json = json.dumps(
            {"evaluation": evaluation},
            indent=2,
            ensure_ascii=False,
        )
        # Drop the outer braces to print just the "evaluation" field.
        print("\n".join(evaluation_json.splitlines()[1:-1]))

        assert_evaluation_structure(evaluation)
        assert evaluation["status"] in {
            "RECOMMENDED_MATCH",
            "POTENTIAL_MATCH",
            "LOW_CONFIDENCE_MATCH",
            "MATCH_FAILURE",
            "match_failure",
            "system_failure",
        }

        score = evaluation["final_composite_score"]
        if score is not None:
            assert isinstance(score, (int, float))
            assert 0 <= score <= 100

# ============================================================
# 2. BEST MATCH SELECTION
# ============================================================

def test_get_best_match(logic_manager):

    ai_result_list = load_test_data("success.json")

    result = logic_manager.get_best_match(
        ai_result_list,
        lost_report_date=LOST_REPORT_DATE
    )

    if result is not None:
        assert "report" in result
        assert "evaluation" in result

        assert_evaluation_structure(result["evaluation"])


# ============================================================
# 3. TIE SCORE SELECTION
# ============================================================

def test_tie_score(logic_manager):

    ai_result_list = load_test_data("tie_score.json")

    result = logic_manager.get_best_match(
        ai_result_list,
        lost_report_date=LOST_REPORT_DATE
    )

    assert result is not None

    # Find the first valid evaluation.
    first_valid_report = None

    for ai_result in ai_result_list:

        evaluation = logic_manager.matcher.evaluate_analysis(
            ai_result,
            LOST_REPORT_DATE
        )

        if evaluation["status"] not in (
            "system_failure",
            "match_failure"
        ):
            first_valid_report = ai_result
            break

    assert first_valid_report is not None
    assert result["report"] == first_valid_report


# ============================================================
# 4. IMPOSSIBLE TIMELINE
# ============================================================

def test_impossible_timeline(logic_manager):

    ai_result = {
        "date": "10-10-2026",
        "similarity_analysis": {
            "similarity_score": 95,
            "color_match": "match",
            "material_match": "match",
            "brand_match": "match",
            "location_match": "match",
            "feature_overlap_match": [
                "logo",
                "shape"
            ]
        }
    }

    lost_report_date = "15-10-2026"

    evaluation = logic_manager.matcher.evaluate_analysis(
        ai_result,
        lost_report_date
    )

    assert evaluation["status"] == "match_failure"

    assert evaluation["final_composite_score"] == 0.0

    assert (
        "TEMPORAL_PARADOX_VETO"
        in evaluation["triggered_rules_list"]
    )


# ============================================================
# 5. THRESHOLD CONFIGURATION INTEGRATION
# ============================================================

def test_logic_manager_uses_custom_threshold_config():

    config = ThresholdConfig(
        reject_threshold=40,
        high_threshold=90,
        min_feature_strong_match=2,
        min_feature_excellent_match=4
    )

    manager = LogicManager(threshold_config=config)

    assert manager.matcher.threshold_config is config

    assert manager.matcher.threshold_config.reject_threshold == 40
    assert manager.matcher.threshold_config.high_threshold == 90


def test_logic_manager_uses_default_threshold_config():

    manager = LogicManager()

    assert manager.matcher.threshold_config.reject_threshold == 50
    assert manager.matcher.threshold_config.high_threshold == 80
def test_location_config_enabled_applies_location_penalty():
    config = ThresholdConfig()
    config.consider_location = True

    logic_manager = LogicManager(threshold_config=config)

    ai_result = {
        "similarity_analysis": {
            "similarity_score": 70,
            "color_match": "match",
            "material_match": "match",
            "brand_match": "match",
            "location_match": "not match",
            "feature_overlap_match": []
        }
    }

    result = logic_manager.matcher.evaluate_analysis(ai_result)

    assert "LOCATION_MISMATCH" in result["triggered_rules_list"]


def test_location_config_disabled_ignores_location_penalty():
    config = ThresholdConfig()
    config.consider_location = False

    logic_manager = LogicManager(threshold_config=config)

    ai_result = {
        "similarity_analysis": {
            "similarity_score": 70,
            "color_match": "match",
            "material_match": "match",
            "brand_match": "match",
            "location_match": "not match",
            "feature_overlap_match": []
        }
    }

    result = logic_manager.matcher.evaluate_analysis(ai_result)

    assert "LOCATION_MISMATCH" not in result["triggered_rules_list"]

@pytest.mark.parametrize("answer, expected_status", [("yes", "closed"), ("no", "active")])
def test_report_match_confirmation_across_layers(
    tmp_path, monkeypatch, logic_manager, answer, expected_status
):
    import data_manager
    from io_manager import IOManager

    monkeypatch.setattr(data_manager, "DATA_FILE", tmp_path / "reports.json")
    monkeypatch.setattr(data_manager, "IMAGE_DIRECTORY", tmp_path / "images")
    monkeypatch.setattr(data_manager, "TEMP_DIRECTORY", tmp_path / "temp")
    data = data_manager.DataManager()

    report = data.save_new_reports({
        "report_type": "found", "category": "bottle", "date": "25-09-2026"
    })
    candidate, = data.get_reports_by_category("bottle")
    # Supply a deterministic analysis at the boundary where AI normally runs.
    candidate["similarity_analysis"] = load_test_data("success.json")[0]["similarity_analysis"]
    match = logic_manager.get_best_match([candidate], LOST_REPORT_DATE)
    assert match is not None
    assert match["report"]["case_id"] == report["case_id"]
    assert match["evaluation"]["status"] == "RECOMMENDED_MATCH"

    confirmed = IOManager().resolve_best_match(match, input_function=lambda prompt: answer)
    assert confirmed is (answer == "yes")
    if confirmed:
        assert data.update_report_status(match["report"]["case_id"], "closed")

    saved, = data_manager.DataManager().load_reports()
    assert saved["status"] == expected_status
    assert "similarity_analysis" not in saved
