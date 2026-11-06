
import json
import tempfile
from pathlib import Path
from datetime import date, timedelta

from data_classes.data_manager_class import DataManager


def run_tests():
    # Use a temporary folder to protect the real database
    with tempfile.TemporaryDirectory() as folder:
        test_folder = Path(folder)
        reports_file = test_folder / "test_reports.json"
        image_directory = test_folder / "images"

        manager = DataManager(reports_file, image_directory)

        # Test 1: Load reports from a missing JSON file
        print("Test 1: Load empty database")
        assert manager.load_reports() == []
        print("PASSED")

        # Test 2: Save a new report
        print("Test 2: Save new report")

        report = manager.save_new_report({
            "report_type": "lost",
            "category": "electronics",
            "description": "Black laptop"
        })

        assert report is not None
        assert report["status"] == "active"
        assert report["case_id"].startswith("CASE-")
        print("PASSED")

        # Test 3: Check JSON file storage
        print("Test 3: Verify JSON storage")

        assert reports_file.is_file()

        with reports_file.open("r", encoding="utf-8") as file:
            saved_reports = json.load(file)

        assert len(saved_reports) == 1
        print("PASSED")

        # Test 4: Retrieve active reports
        print("Test 4: Retrieve active reports")

        active_reports = manager.get_active_reports()

        assert len(active_reports) == 1
        print("PASSED")

        # Test 5: Filter reports by category
        print("Test 5: Filter reports by category")

        matching_reports = manager.get_reports_by_category(
            "electronics"
        )

        assert len(matching_reports) == 1
        print("PASSED")

        # Test 6: Search report by case ID
        print("Test 6: Search report by case ID")

        case_id = report["case_id"]
        found_report = manager.get_report_by_id(case_id)

        assert found_report is not None
        assert found_report["case_id"] == case_id
        print("PASSED")

        # Test 7: Reject invalid report status
        print("Test 7: Reject invalid status")

        result = manager.update_report_status(
            case_id,
            "pending"
        )

        assert result is False
        print("PASSED")

        # Test 8: Close an existing report
        print("Test 8: Update report status")

        result = manager.update_report_status(
            case_id,
            "closed"
        )

        assert result is True

        updated_report = manager.get_report_by_id(case_id)

        assert updated_report["status"] == "closed"
        assert updated_report["closed_date"] == date.today().isoformat()
        print("PASSED")

        # Test 9: Verify closed reports are not active
        print("Test 9: Exclude closed reports")

        assert manager.get_active_reports() == []
        print("PASSED")

        # Test 10: Delete expired reports
        print("Test 10: Delete expired reports")

        reports = manager.load_reports()

        old_date = date.today() - timedelta(days=40)
        reports[0]["closed_date"] = old_date.isoformat()

        assert manager.save_report_list(reports) is True

        deleted_count = manager.delete_expired_reports(30)

        assert deleted_count == 1
        assert manager.load_reports() == []
        print("PASSED")

        # Test 11: Save and retrieve an image
        print("Test 11: Store report image")

        source_image = test_folder / "sample.jpg"
        source_image.write_bytes(b"test image content")

        image_report = manager.save_new_report({
            "report_type": "found",
            "category": "electronics",
            "description": "Found phone",
            "image_path": str(source_image)
        })

        assert image_report is not None

        image_filename = image_report["image_filename"]

        assert image_filename is not None
        assert (image_directory / image_filename).is_file()
        print("PASSED")

        # Test 12: Clear temporary files
        print("Test 12: Clear temporary files")

        temp_directory = test_folder / "temp"
        temp_directory.mkdir()

        temporary_file = temp_directory / "temporary.txt"
        temporary_file.write_text("Temporary data")

        deleted_count = manager.clear_temp_directory(
            temp_directory
        )

        assert deleted_count == 1
        assert not temporary_file.exists()
        print("PASSED")

        # Test 13: Reject invalid JSON data
        print("Test 13: Reject invalid JSON")

        reports_file.write_text(
            "{invalid json",
            encoding="utf-8"
        )

        try:
            manager.load_reports()
            assert False, "Invalid JSON was accepted"
        except json.JSONDecodeError:
            print("PASSED")

    print("\nAll 13 Data Manager tests passed!")


if __name__ == "__main__":
    run_tests()
