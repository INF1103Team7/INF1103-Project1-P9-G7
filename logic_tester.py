import json
import os

from logic_manager import *


# ----------------------------------------
# Test Configuration
# ----------------------------------------

TEST_FOLDER = "logic_test_data"

TEST_FILES = [
    "success.json",
    "strong_match.json",
    "weak_match.json",
    "multi_rule.json",
    "wrong_format.json",
    "tie_score.json",
    "missing_keys.json",
]


# ----------------------------------------
# Run One Test File
# ----------------------------------------

def run_test(test_file):

    file_path = os.path.join(TEST_FOLDER, test_file)

    print("\n========================================")
    print(f"TESTING: {test_file}")
    print("========================================")

    # Load JSON test file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            ai_result_list = json.load(f)

    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        return

    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        return

    print(f"[+] Loaded {len(ai_result_list)} AI results.")

    # ----------------------------------------
    # Evaluate Every Report
    # ----------------------------------------

    for index, ai_result in enumerate(ai_result_list, start=1):

        print("\n----------------------------------------")
        print(f"REPORT {index}")
        print("----------------------------------------")

        evaluation = evaluate_analysis(ai_result)

        print(f"Case ID: {ai_result.get('case_id')}")
        print(f"Status: {evaluation['status']}")
        print(f"Final Score: {evaluation['final_composite_score']}")

        print("\nMatched Rules:")
        print(evaluation["matched_rules_list"])

        print("\nMismatched Rules:")
        print(evaluation["mismatched_rules_list"])

        print("\nTriggered Rules:")
        print(evaluation["triggered_rules_list"])

        print("\nSummary:")
        print(evaluation["evaluation_summary"])

    # ----------------------------------------
    # Find Best Match
    # ----------------------------------------

    result = get_best_match(ai_result_list)

    print("\n========================================")
    print("BEST MATCH")
    print("========================================")

    if result is None:
        print("No valid best match found.")
        return

    print(f"Case ID: {result['report'].get('case_id')}")
    print(f"Status: {result['evaluation']['status']}")
    print(f"Final Score: {result['evaluation']['final_composite_score']}")

    print("\nBest Match Report:")
    print(json.dumps(result["report"], indent=4))

    print("\nBest Match Evaluation:")
    print(json.dumps(result["evaluation"], indent=4))


# ----------------------------------------
# Main
# ----------------------------------------

if __name__ == "__main__":

    print("\n========================================")
    print("       LOGIC MANAGER TEST SUITE")
    print("========================================")

    for test_file in TEST_FILES:
        run_test(test_file)

    print("\n========================================")
    print("          TESTING COMPLETE")
    print("========================================")