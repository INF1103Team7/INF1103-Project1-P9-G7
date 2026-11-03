import subprocess
import sys
import json
from pathlib import Path
from logic_manager import LogicManager

from logic_classes.threshold_file import ThresholdFile
from logic_classes.threshold_config import ThresholdConfig


def run_threshold_config_test(config, file_manager):

    print("\n=== THRESHOLD CONFIGURATION ===")

    while True:
        print("\n========== THRESHOLD MENU ==========")
        print(f"1. Update high threshold ({config.get_high_threshold()})")
        print(f"2. Update reject threshold ({config.get_reject_threshold()})")
        print(
            f"3. Update strong match minimum "
            f"({config.get_min_feature_strong_match()})"
        )
        print(
            f"4. Update excellent match minimum "
            f"({config.get_min_feature_excellent_match()})"
        )
        print("5. Display all thresholds")
        print("6. Save thresholds")
        print("7. Reset thresholds")
        print("8. Continue to testing")
        print("====================================")

        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            value = int(input("New high threshold: "))
            print(config.update_high_threshold(value))

        elif choice == "2":
            value = int(input("New reject threshold: "))
            print(config.update_reject_threshold(value))

        elif choice == "3":
            value = int(input("New strong match minimum: "))
            print(config.update_min_feature_strong_match(value))

        elif choice == "4":
            value = int(input("New excellent match minimum: "))
            print(config.update_min_feature_excellent_match(value))

        elif choice == "5":
            print("\nCurrent thresholds:")
            print("High:", config.get_high_threshold())
            print("Reject:", config.get_reject_threshold())
            print("Strong:", config.get_min_feature_strong_match())
            print("Excellent:", config.get_min_feature_excellent_match())

        elif choice == "6":
            print(file_manager.save(config))

        elif choice == "7":
            confirmation = input(
                "Reset all thresholds to defaults? (y/n): "
            ).strip().lower()

            if confirmation == "y":
                print(config.reset_all_threshold())

        elif choice == "8":
            print("\nContinuing to automated testing...")
            break

        else:
            print("Invalid choice. Please enter 1-8.")
def run_import_test():
    print("\n=== STEP 1: Testing imports ===")

    try:
        from logic_classes.matcher import Matcher
        from logic_classes.match_selector import MatchSelector
        from logic_classes.threshold_config import ThresholdConfig
        from logic_classes.threshold_file import ThresholdFile
        from logic_manager import LogicManager

        print("[PASS] LogicManager imported")
        print("[PASS] Matcher imported")
        print("[PASS] MatchSelector imported")
        print("[PASS] ThresholdConfig imported")
        print("[PASS] ThresholdFile imported")

        # Create the threshold configuration.
        config = ThresholdConfig()
        file_manager = ThresholdFile()

        # Load previously saved thresholds.
        saved_data = file_manager.load()

        if saved_data is not None:
            config.load_thresholds(saved_data)
            print("[PASS] Saved thresholds loaded")
        else:
            print("[INFO] Using default thresholds")

        # Pass the same configuration to LogicManager.
        manager = LogicManager(threshold_config=config)

        # Verify that all classes share the same configuration.
        assert manager.matcher.threshold_config is config

        print("[PASS] LogicManager instantiated")
        print("[PASS] Threshold configuration connected")

        return manager, config, file_manager

    except Exception as error:
        print(f"[FAIL] Import/initialisation error: {error}")
        return None, None, None
def run_pytest():
    print("\n=== STEP 2: Running automated tests ===")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v"],
        check=False
    )

    if result.returncode == 0:
        print("\n[PASS] All pytest tests passed!")
        return True

    print("\n[FAIL] Some pytest tests failed.")
    return False

def check_impossible_timeline(manager):

    print("\n=== IMPOSSIBLE TIMELINE TEST ===")

    ai_result = {
        "date": "10-10-2026",
        "similarity_analysis": {
            "similarity_score": 95,
            "color_match": "match",
            "material_match": "match",
            "brand_match": "match",
            "location_match": "match",
            "feature_overlap_match": ["logo", "shape"]
        }
    }

    lost_report_date = "15-10-2026"

    evaluation = manager.matcher.evaluate_analysis(
        ai_result,
        lost_report_date
    )

    print("Status:", evaluation["status"])
    print("Score:", evaluation["final_composite_score"])
    print("Triggered:", evaluation["triggered_rules_list"])
    print("Summary:", evaluation["evaluation_summary"])

    assert evaluation["status"] == "match_failure"
    assert "TEMPORAL_PARADOX_VETO" in evaluation["triggered_rules_list"]

    print("[PASS] Impossible timeline detected!")
def display_report(manager, ai_result, filename):

    evaluation = manager.matcher.evaluate_analysis(ai_result)

    print(
        f"{filename:<25} | "
        f"{evaluation['status']:<20} | "
        f"{evaluation['final_composite_score']}"
    )

    print("  Matched:", ", ".join(evaluation["matched_rules_list"]))
    print("  Mismatched:", ", ".join(evaluation["mismatched_rules_list"]))
    print("  Triggered:", ", ".join(evaluation["triggered_rules_list"]))
    print("  Summary:", evaluation["evaluation_summary"])
def display_best_match(manager, ai_results):

    best_match = manager.get_best_match(ai_results)

    print("\n--- FINAL BEST MATCH ---")

    if best_match is None:
        print("No suitable match found.")
        return

    report = best_match["report"]
    evaluation = best_match["evaluation"]

    # Find the report's position in the original list.
    report_number = next(
        (i for i, item in enumerate(ai_results, 1)
         if item is report),
        None
    )

    print(f"Final Report: Report {report_number}")
    print("Status:", evaluation["status"])
    print("Score:", evaluation["final_composite_score"])
    print("Summary:", evaluation["evaluation_summary"])


def run_json_report_test(manager):
    print("\n=== STEP 3: Displaying JSON matching reports ===")

    data_folder = Path(__file__).parent / "logic_test_data"

    if not data_folder.exists():
        print(f"[FAIL] Folder not found: {data_folder}")
        return False

    json_files = sorted(data_folder.glob("*.json"))

    if not json_files:
        print("[WARNING] No JSON files found.")
        return False

    print(f"Found {len(json_files)} JSON file(s).")

    passed = 0
    failed = 0
    print("\n" + "=" * 90)
    print("INDIVIDUAL REPORT EVALUATIONS")
    print("=" * 90)
    print(f"{'JSON FILE':<25} | {'STATUS':<20} | {'SCORE':<10}")
    print("-" * 90)

    for file_path in json_files:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                file_data = json.load(file)

            # Support either one AI result or a list of AI results.
            if isinstance(file_data, list):
                ai_results = file_data
            else:
                ai_results = [file_data]

            print(f"\nFound {len(ai_results)} report(s) in {file_path.name}")

            # Show final best report first.
            display_best_match(manager, ai_results)

            # Then show individual reports.
            for index, ai_result in enumerate(ai_results, start=1):

                print(f"\nREPORT {index} OF {len(ai_results)}")

                try:
                    display_report(manager, ai_result, file_path.name)
                    passed += 1

                except Exception as error:
                    print(f"[FAIL] Could not evaluate report: {error}")
                    failed += 1
        except (json.JSONDecodeError, OSError) as error:
            print(f"[FAIL] Could not read {file_path.name}: {error}")
            failed += 1

    print("\n=== JSON REPORT TEST SUMMARY ===")
    print(f"Successfully evaluated: {passed}")
    print(f"Failed or skipped: {failed}")

    return passed > 0 and failed == 0
if __name__ == "__main__":

    manager, config, file_manager = run_import_test()

    if manager is not None:

        # STEP 2: Configure thresholds.
        run_threshold_config_test(config, file_manager)

        # STEP 3: Run automated tests.
        tests_passed = run_pytest()

        # STEP 4: Test impossible timeline.
        check_impossible_timeline(manager)

        # STEP 5: Test JSON reports.
        reports_passed = run_json_report_test(manager)

    else:
        tests_passed = False
        reports_passed = False

        print("\nTesting skipped because imports failed.")

    print("\n" + "=" * 45)
    print("FINAL RESULT")
    print("=" * 45)

    print(f"Import Test: {'PASS' if manager is not None else 'FAIL'}")
    print(f"Pytest: {'PASS' if tests_passed else 'FAIL'}")
    print(f"JSON Reports: {'PASS' if reports_passed else 'FAIL'}")

    if manager is not None and tests_passed and reports_passed:
        print("\nEverything passed! Ready to commit and push.")
    else:
        print("\nSomething failed. Review the output above.")