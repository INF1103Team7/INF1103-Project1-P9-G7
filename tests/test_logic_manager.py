import json
from pathlib import Path

import pytest

from logic_manager import LogicManager


TEST_FOLDER = Path(__file__).parent.parent / "logic_test_data"


@pytest.fixture
def logic_manager():
    return LogicManager()


def load_test_data(filename):
    file_path = TEST_FOLDER / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# ----------------------------------------
# Test Individual Evaluations
# ----------------------------------------

@pytest.mark.parametrize("filename", [
    "success.json",
    "strong_match.json",
    "weak_match.json",
    "multi_rule.json",
    "wrong_format.json",
    "missing_keys.json",
])
def test_evaluate_analysis(logic_manager, filename):

    ai_result_list = load_test_data(filename)

    for ai_result in ai_result_list:

        evaluation = logic_manager.matcher.evaluate_analysis(ai_result)

        assert isinstance(evaluation, dict)

        assert "status" in evaluation
        assert "final_composite_score" in evaluation
        assert "matched_rules_list" in evaluation
        assert "mismatched_rules_list" in evaluation
        assert "triggered_rules_list" in evaluation
        assert "evaluation_summary" in evaluation


# ----------------------------------------
# Test Best Match Selection
# ----------------------------------------

def test_get_best_match(logic_manager):

    ai_result_list = load_test_data("success.json")

    result = logic_manager.get_best_match(ai_result_list)

    if result is not None:
        assert "report" in result
        assert "evaluation" in result


# ----------------------------------------
# Test Tie Score
# ----------------------------------------

def test_tie_score(logic_manager):

    ai_result_list = load_test_data("tie_score.json")

    result = logic_manager.get_best_match(ai_result_list)

    assert result is not None

    # The first valid report should win when scores are tied.
    # Compare against the first valid report in the test data.
    first_valid_report = None

    for ai_result in ai_result_list:

        evaluation = logic_manager.matcher.evaluate_analysis(ai_result)

        if evaluation["status"] not in ("system_failure", "match_failure"):
            first_valid_report = ai_result
            break

    assert result["report"] == first_valid_report