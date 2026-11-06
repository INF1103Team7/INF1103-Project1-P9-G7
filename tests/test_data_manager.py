
import json
import pytest
from datetime import date, timedelta

from data_classes.data_manager_class import DataManager


# --------------------------------------------------
# Fixtures
# --------------------------------------------------

@pytest.fixture
def reports_file(tmp_path):
    return tmp_path / "test_reports.json"


@pytest.fixture
def image_directory(tmp_path):
    return tmp_path / "images"


@pytest.fixture
def manager(reports_file, image_directory):
    return DataManager(reports_file, image_directory)


# --------------------------------------------------
# Test 1: Load reports from a missing JSON file
# --------------------------------------------------

def test_load_empty_database(manager):
    assert manager.load_reports() == []


# --------------------------------------------------
# Test 2: Save a new report
# --------------------------------------------------

def test_save_new_report(manager):
    report = manager.save_new_report({
        "report_type": "lost",
        "category": "electronics",
        "description": "Black laptop"
    })

    assert report is not None
    assert report["status"] == "active"
    assert report["case_id"].startswith("CASE-")


# --------------------------------------------------
# Test 3: Verify JSON file storage
# --------------------------------------------------

def test_verify_json_storage(manager, reports_file):
    manager.save_new_report({
        "report_type": "lost",
        "category": "electronics",
        "description": "Black laptop"
    })

    assert reports_file.is_file()

    with reports_file.open("r", encoding="utf-8") as file:
        saved_reports = json.load(file)

    assert len(saved_reports) == 1


# --------------------------------------------------
# Test 4: Retrieve active reports
# --------------------------------------------------

def test_get_active_reports(manager):
    manager.save_new_report({
        "report_type": "lost",
        "category": "electronics",
        "description": "Black laptop"
    })

    active_reports = manager.get_active_reports()

    assert len(active_reports) == 1
    assert active_reports[0]["status"] == "active"


# --------------------------------------------------
# Test 5: Filter reports by category
# --------------------------------------------------

def test_get_reports_by_category(manager):
    manager.save_new_report({
        "report_type": "lost",
        "category": "electronics",
        "description": "Black laptop"
    })

    matching_reports = manager.get_reports_by_category("electronics")

    assert len(matching_reports) == 1
    assert matching_reports[0]["category"] == "electronics"


# --------------------------------------------------
# Test 6: Search report by case ID
# --------------------------------------------------

def test_get_report_by_id(manager):
    report = manager.save_new_report({
        "report_type": "lost",
        "category": "electronics",
        "description": "Black laptop"
    })

    case_id = report["case_id"]
    found_report = manager.get_report_by_id(case_id)

    assert found_report is not None
    assert found_report["case_id"] == case_id


# --------------------------------------------------
# Test 7: Reject invalid report status
# --------------------------------------------------

def test_reject_invalid_status(manager):
    report = manager.save_new_report({
        "report_type": "lost",
        "category": "electronics",
        "description": "Black laptop"
    })

    result = manager.update_report_status(
        report["case_id"],
        "pending"
    )

    assert result is False


# --------------------------------------------------
# Test 8: Close an existing report
# --------------------------------------------------

def test_update_report_status(manager):
    report = manager.save_new_report({
        "report_type": "lost",
        "category": "electronics",
        "description": "Black laptop"
    })

    case_id = report["case_id"]

    result = manager.update_report_status(case_id, "closed")

    assert result is True

    updated_report = manager.get_report_by_id(case_id)

    assert updated_report["status"] == "closed"
    assert updated_report["closed_date"] == date.today().isoformat()


# --------------------------------------------------
# Test 9: Verify closed reports are not active
# --------------------------------------------------

def test_exclude_closed_reports(manager):
    report = manager.save_new_report({
        "report_type": "lost",
        "category": "electronics",
        "description": "Black laptop"
    })

    manager.update_report_status(report["case_id"], "closed")

    assert manager.get_active_reports() == []


# --------------------------------------------------
# Test 10: Delete expired reports
# --------------------------------------------------

def test_delete_expired_reports(manager):
    report = manager.save_new_report({
        "report_type": "lost",
        "category": "electronics",
        "description": "Black laptop"
    })

    case_id = report["case_id"]

    manager.update_report_status(case_id, "closed")

    reports = manager.load_reports()

    old_date = date.today() - timedelta(days=40)
    reports[0]["closed_date"] = old_date.isoformat()

    assert manager.save_report_list(reports) is True

    deleted_count = manager.delete_expired_reports(30)

    assert deleted_count == 1
    assert manager.load_reports() == []


# --------------------------------------------------
# Test 11: Save and retrieve an image
# --------------------------------------------------

def test_store_report_image(manager, tmp_path, image_directory):
    source_image = tmp_path / "sample.jpg"
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


# --------------------------------------------------
# Test 12: Clear temporary files
# --------------------------------------------------

def test_clear_temp_directory(manager, tmp_path):
    temp_directory = tmp_path / "temp"
    temp_directory.mkdir()

    temporary_file = temp_directory / "temporary.txt"
    temporary_file.write_text("Temporary data", encoding="utf-8")

    deleted_count = manager.clear_temp_directory(temp_directory)

    assert deleted_count == 1
    assert not temporary_file.exists()


# --------------------------------------------------
# Test 13: Reject invalid JSON data
# --------------------------------------------------

def test_reject_invalid_json(manager, reports_file):
    reports_file.write_text(
        "{invalid json",
        encoding="utf-8"
    )

    with pytest.raises(json.JSONDecodeError):
        manager.load_reports()