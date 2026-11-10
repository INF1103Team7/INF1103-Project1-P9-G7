
import json
import pytest
from datetime import date, timedelta
from pathlib import Path
from data_classes.data_manager_service import DataManager
from data_classes.data_json_report_storage import JsonReportStorage
from data_classes.data_report import Report
import data_manager
from unittest.mock import Mock
import shutil
import os
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


def test_store_image_invalid_type(manager, capsys):
    result = manager.store_image(123, "CASE-001")

    captured = capsys.readouterr()

    assert result is None
    assert "Invalid image path" in captured.out


def test_store_image_invalid_extension(manager, tmp_path, capsys):
    source_file = tmp_path / "document.txt"
    source_file.write_text("Not an image")

    result = manager.store_image(
        str(source_file),
        "CASE-001"
    )

    captured = capsys.readouterr()

    assert result is None
    assert "Only JPG, JPEG and PNG images are allowed" in captured.out


def test_store_image_missing_file(manager, tmp_path, capsys):
    missing_image = tmp_path / "missing.jpg"

    result = manager.store_image(
        str(missing_image),
        "CASE-001"
    )

    captured = capsys.readouterr()

    assert result is None
    assert "Image not found:" in captured.out


@pytest.mark.parametrize(
    "invalid_days",
    [-1, "30", 3.5, True, None]
)
def test_delete_expired_reports_invalid_retention(manager, invalid_days):
    with pytest.raises(
        ValueError,
        match="Retention days must be a non-negative integer"
    ):
        manager.delete_expired_reports(invalid_days)


def test_delete_expired_reports_none_expired(manager):
    report = manager.save_new_report({
        "report_type": "lost",
        "category": "bottle",
        "description": "Blue water bottle"
    })

    result = manager.delete_expired_reports(30)

    assert result == 0
    assert manager.get_report_by_id(report["case_id"]) is not None


def test_delete_expired_reports_invalid_closed_date(manager, capsys):
    report = manager.save_new_report({
        "report_type": "lost",
        "category": "electronics",
        "description": "Black laptop"
    })

    manager.update_report_status(report["case_id"], "closed")

    reports = manager.load_reports()
    reports[0]["closed_date"] = "invalid-date"
    manager.save_report_list(reports)

    result = manager.delete_expired_reports(30)

    captured = capsys.readouterr()

    assert result == 0
    assert "Invalid closed date in report" in captured.out
    assert len(manager.load_reports()) == 1


def test_store_image_same_source_destination(manager, image_directory):
    image_directory.mkdir(parents=True, exist_ok=True)

    source_image = image_directory / "CASE-001.jpg"
    source_image.write_bytes(b"test image")

    result = manager.store_image(
        source_image,
        "CASE-001"
    )

    assert result == "CASE-001.jpg"
    assert source_image.read_bytes() == b"test image"


def test_store_image_copy_error(manager, tmp_path, monkeypatch, capsys):
    source_image = tmp_path / "sample.jpg"
    source_image.write_bytes(b"test image")

    def fake_copy(source, destination):
        raise OSError("Copy failed")

    monkeypatch.setattr(
        "data_classes.data_manager_class.shutil.copy2",
        fake_copy
    )

    result = manager.store_image(
        source_image,
        "CASE-001"
    )

    captured = capsys.readouterr()

    assert result is None
    assert "Error saving image: Copy failed" in captured.out


def test_delete_expired_report_image(manager, image_directory):
    image_directory.mkdir(parents=True, exist_ok=True)

    image_file = image_directory / "CASE-001.jpg"
    image_file.write_bytes(b"test image")

    report = manager.save_new_report({
        "report_type": "lost",
        "category": "bottle",
        "description": "Blue water bottle"
    })

    reports = manager.load_reports()

    reports[0]["status"] = "closed"
    reports[0]["closed_date"] = (
        date.today() - timedelta(days=40)
    ).isoformat()
    reports[0]["image_filename"] = image_file.name

    manager.save_report_list(reports)

    result = manager.delete_expired_reports(30)

    assert result == 1
    assert not image_file.exists()
    assert manager.load_reports() == []


def test_clear_temp_directory_missing(manager, tmp_path):
    missing_directory = tmp_path / "missing_temp"

    result = manager.clear_temp_directory(missing_directory)

    assert result == 0


def test_clear_temp_directory_not_directory(manager, tmp_path, capsys):
    temp_file = tmp_path / "temp.txt"
    temp_file.write_text("Temporary data")

    result = manager.clear_temp_directory(temp_file)

    captured = capsys.readouterr()

    assert result == 0
    assert "Temporary path is not a directory" in captured.out


def test_delete_multiple_expired_report_images(manager, image_directory):
    image_directory.mkdir(parents=True, exist_ok=True)

    image1 = image_directory / "first.jpg"
    image2 = image_directory / "second.jpg"

    image1.write_bytes(b"first image")
    image2.write_bytes(b"second image")

    old_date = (date.today() - timedelta(days=40)).isoformat()

    reports = [
        {
            "case_id": "CASE-001",
            "status": "closed",
            "closed_date": old_date,
            "image_filename": "first.jpg"
        },
        {
            "case_id": "CASE-002",
            "status": "closed",
            "closed_date": old_date,
            "image_filename": "second.jpg"
        }
    ]

    manager.save_report_list(reports)

    result = manager.delete_expired_reports(30)

    assert result == 2
    assert manager.load_reports() == []
    assert not image1.exists()
    assert not image2.exists()


def test_clear_temp_directory_delete_error(
    manager, tmp_path, monkeypatch, capsys
):
    temp_directory = tmp_path / "temp"
    temp_directory.mkdir()

    temp_file = temp_directory / "test.txt"
    temp_file.write_text("Temporary data")

    original_unlink = Path.unlink

    def fake_unlink(self, *args, **kwargs):
        if self == temp_file:
            raise OSError("Permission denied")

        return original_unlink(self, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fake_unlink)

    result = manager.clear_temp_directory(temp_directory)

    captured = capsys.readouterr()

    assert result == 0
    assert "Error deleting temp file: Permission denied" in captured.out
    assert temp_file.exists()


def test_clear_temp_directory_access_error(
    manager, tmp_path, monkeypatch, capsys
):
    temp_directory = tmp_path / "temp"
    temp_directory.mkdir()

    original_iterdir = Path.iterdir

    def fake_iterdir(self):
        if self == temp_directory:
            raise OSError("Access denied")

        return original_iterdir(self)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)

    result = manager.clear_temp_directory(temp_directory)

    captured = capsys.readouterr()

    assert result == 0
    assert "Error accessing temporary directory: Access denied" in captured.out


def test_load_reports_not_list(reports_file):
    storage = JsonReportStorage(reports_file)

    reports_file.write_text(
        json.dumps({"case_id": "CASE-001"}),
        encoding="utf-8"
    )

    with pytest.raises(
        ValueError,
        match="Reports must be stored as a list"
    ):
        storage.load_reports()


def test_load_reports_invalid_item(reports_file):
    storage = JsonReportStorage(reports_file)

    reports_file.write_text(
        json.dumps([
            {"case_id": "CASE-001"},
            "invalid report"
        ]),
        encoding="utf-8"
    )

    with pytest.raises(
        ValueError,
        match="Each report must be a dictionary"
    ):
        storage.load_reports()


def test_save_reports_invalid_data(reports_file, capsys):
    storage = JsonReportStorage(reports_file)

    reports = [
        {
            "case_id": "CASE-001",
            "invalid_value": {1, 2, 3}
        }
    ]

    result = storage.save_reports(reports)

    captured = capsys.readouterr()

    assert result is False
    assert "Error saving reports:" in captured.out


def test_report_getters():
    report = Report({
        "case_id": "CASE-001",
        "category": "bottle",
        "status": "active"
    })

    assert report.get_case_id() == "CASE-001"
    assert report.get_category() == "bottle"
    assert report.get_status() == "active"


@pytest.mark.parametrize("invalid_status", [
    123,
    None,
    True,
    ["closed"]
])
def test_report_update_status_invalid_type(invalid_status):
    report = Report({
        "case_id": "CASE-001",
        "status": "active"
    })

    result = report.update_status(invalid_status)

    assert result is False
    assert report.get_status() == "active"


def test_report_reopen_closed():
    report = Report({
        "case_id": "CASE-001",
        "status": "closed",
        "closed_date": "2026-01-01"
    })

    result = report.update_status("active")

    assert result is True
    assert report.get_status() == "active"
    assert "closed_date" not in report.to_dict()


def test_save_new_report_invalid_image_path(manager):
    report_data = {
        "case_id": "CASE-001",
        "category": "bottle",
        "image_path": 123
    }

    with pytest.raises(
        ValueError,
        match="Image path must be a string"
    ):
        manager.save_new_report(report_data)

    assert manager.load_reports() == []


def test_save_new_report_save_failure(manager, monkeypatch):
    report_data = {
        "case_id": "CASE-001",
        "category": "bottle"
    }

    def fake_save(reports):
        return False

    monkeypatch.setattr(manager, "save_report_list", fake_save)

    result = manager.save_new_report(report_data)

    assert result is None

def test_update_report_status_nonexistent(manager):
    report_data = {
        "case_id": "CASE-001",
        "category": "bottle"
    }

    manager.save_new_report(report_data)

    result = manager.update_report_status("CASE-999", "closed")

    assert result is False

    saved_report = manager.get_report_by_id("CASE-001")

    assert saved_report["status"] == "active"
    assert saved_report.get("closed_date") is None

def test_get_report_by_id_nonexistent(manager):
    manager.save_new_report({
        "case_id": "CASE-001",
        "category": "bottle"
    })

    result = manager.get_report_by_id("CASE-999")

    assert result is None


def test_delete_expired_reports_save_failure(manager, monkeypatch):
    old_date = (date.today() - timedelta(days=40)).isoformat()

    manager.save_new_report({
        "case_id": "CASE-001",
        "category": "bottle",
        "status": "closed",
        "closed_date": old_date
    })

    monkeypatch.setattr(manager, "save_report_list", lambda reports: False)

    result = manager.delete_expired_reports(retention_days=30)

    assert result == 0
    assert manager.get_report_by_id("CASE-001") is not None


def test_delete_expired_reports_invalid_image_filename(manager, tmp_path, capsys):
    old_date = (date.today() - timedelta(days=40)).isoformat()

    outside_image = tmp_path / "outside.jpg"
    outside_image.write_bytes(b"test image")

    manager.save_new_report({
        "case_id": "CASE-001",
        "status": "closed",
        "closed_date": old_date,
        "image_filename": "../outside.jpg"
    })

    result = manager.delete_expired_reports(retention_days=30)

    captured = capsys.readouterr()

    assert result == 1
    assert outside_image.exists()
    assert "Invalid image filename:" in captured.out


def test_delete_expired_reports_image_delete_error(
    manager, tmp_path, monkeypatch, capsys
):
    old_date = (date.today() - timedelta(days=40)).isoformat()

    manager._image_directory.mkdir(parents=True, exist_ok=True)

    image_file = manager._image_directory / "CASE-001.jpg"
    image_file.write_bytes(b"test image")

    manager.save_new_report({
        "case_id": "CASE-001",
        "status": "closed",
        "closed_date": old_date,
        "image_filename": "CASE-001.jpg"
    })

    original_unlink = Path.unlink

    def fake_unlink(self, *args, **kwargs):
        if self == image_file:
            raise OSError("Permission denied")
        return original_unlink(self, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fake_unlink)

    result = manager.delete_expired_reports(retention_days=30)

    captured = capsys.readouterr()

    assert result == 1
    assert image_file.exists()
    assert "Error deleting image: Permission denied" in captured.out


# ============================================================
# Tests for data_manager.py (function-based interface)
# ============================================================


# 1. Case ID generation
def test_function_create_case_id():
    case_id = data_manager.create_case_id()

    assert case_id.startswith(f"CASE-{date.today():%Y%m%d}-")
    assert len(case_id.split("-")[-1]) == 6


def test_function_create_case_id_unique():
    first_id = data_manager.create_case_id()
    second_id = data_manager.create_case_id()

    assert first_id != second_id


# 2. Load reports without migration
def test_function_load_reports_no_migration(tmp_path):
    reports_file = tmp_path / "reports.json"

    reports = [
        {"case_id": "CASE-001", "status": "active"}
    ]

    reports_file.write_text(json.dumps(reports), encoding="utf-8")

    result = data_manager.load_reports(reports_file)

    assert result == reports


# 3. Load reports and migrate old image filenames
def test_function_load_reports_migration(tmp_path):
    reports_file = tmp_path / "reports.json"
    image_directory = tmp_path / "images"
    image_directory.mkdir()

    old_image = image_directory / "old.jpg"
    old_image.write_bytes(b"image data")

    reports = [
        {
            "category": "bottle",
            "image_filename": "old.jpg"
        }
    ]

    reports_file.write_text(json.dumps(reports), encoding="utf-8")

    result = data_manager.load_reports(reports_file)

    assert len(result) == 1
    assert result[0]["case_id"].startswith("CASE-")
    assert result[0]["image_filename"].endswith(".jpg")

    new_image = image_directory / result[0]["image_filename"]

    assert new_image.exists()
    assert not old_image.exists()

    saved_reports = json.loads(reports_file.read_text(encoding="utf-8"))
    assert saved_reports == result


# 4. Migration skips reports that already have case IDs
def test_function_migration_existing_case_id(tmp_path):
    reports = [
        {
            "case_id": "CASE-001",
            "image_filename": "old.jpg"
        }
    ]

    result = data_manager._migrate_old_image_names(
        reports, tmp_path
    )

    assert result is False
    assert reports[0]["image_filename"] == "old.jpg"


# 5. Migration skips invalid image filenames
@pytest.mark.parametrize("filename", [None, 123, True])
def test_function_migration_invalid_filename(tmp_path, filename):
    reports = [{"image_filename": filename}]

    result = data_manager._migrate_old_image_names(
        reports, tmp_path
    )

    assert result is False
    assert "case_id" not in reports[0]


# 6. Migration skips missing image files
def test_function_migration_missing_image(tmp_path):
    reports = [{"image_filename": "missing.jpg"}]

    result = data_manager._migrate_old_image_names(
        reports, tmp_path
    )

    assert result is False
    assert "case_id" not in reports[0]


# 7. Migration fails to save updated reports
def test_function_load_reports_migration_save_failure(
    tmp_path, monkeypatch
):
    reports_file = tmp_path / "reports.json"
    image_directory = tmp_path / "images"
    image_directory.mkdir()

    (image_directory / "old.jpg").write_bytes(b"image")

    reports_file.write_text(
        json.dumps([{"image_filename": "old.jpg"}]),
        encoding="utf-8"
    )

    monkeypatch.setattr(
        data_manager.DataManager,
        "save_report_list",
        lambda self, reports: False
    )

    with pytest.raises(
        OSError,
        match="Unable to save migrated reports"
    ):
        data_manager.load_reports(reports_file)


# 8. Save a new report through the wrapper
def test_function_save_new_reports(tmp_path):
    reports_file = tmp_path / "reports.json"
    image_directory = tmp_path / "images"

    report = {
        "case_id": "CASE-001",
        "category": "bottle"
    }

    result = data_manager.save_new_reports(
        report, reports_file, image_directory
    )

    assert result["case_id"] == "CASE-001"
    assert result["status"] == "active"

    saved = json.loads(reports_file.read_text(encoding="utf-8"))
    assert len(saved) == 1


# 9. Reject invalid image path through the wrapper
def test_function_save_new_reports_invalid_path(tmp_path):
    reports_file = tmp_path / "reports.json"

    report = {
        "case_id": "CASE-001",
        "image_path": 123
    }

    with pytest.raises(
        ValueError,
        match="Image path must be a string"
    ):
        data_manager.save_new_reports(
            report, reports_file, tmp_path / "images"
        )

    assert not reports_file.exists()


# 10. Save report list through the wrapper
def test_function_save_report_list(tmp_path, monkeypatch):
    reports_file = tmp_path / "reports.json"

    monkeypatch.setattr(data_manager, "DATA_FILE", reports_file)

    reports = [{"case_id": "CASE-001"}]

    result = data_manager.save_report_list(reports)

    assert result is True
    assert json.loads(reports_file.read_text(encoding="utf-8")) == reports


# 11. Get active reports through the wrapper
def test_function_get_active_reports(tmp_path, monkeypatch):
    reports_file = tmp_path / "reports.json"
    monkeypatch.setattr(data_manager, "DATA_FILE", reports_file)

    reports_file.write_text(json.dumps([
        {"case_id": "CASE-001", "status": "active"},
        {"case_id": "CASE-002", "status": "closed"}
    ]), encoding="utf-8")

    result = data_manager.get_active_reports()

    assert len(result) == 1
    assert result[0]["case_id"] == "CASE-001"


# 12. Filter reports by category through the wrapper
def test_function_get_reports_by_category(tmp_path, monkeypatch):
    reports_file = tmp_path / "reports.json"
    monkeypatch.setattr(data_manager, "DATA_FILE", reports_file)

    reports_file.write_text(json.dumps([
        {"case_id": "CASE-001", "category": "bottle", "status": "active"},
        {"case_id": "CASE-002", "category": "bag", "status": "active"},
        {"case_id": "CASE-003", "category": "bottle", "status": "closed"}
    ]), encoding="utf-8")

    result = data_manager.get_reports_by_category("bottle")

    assert len(result) == 1
    assert result[0]["case_id"] == "CASE-001"


# 13. Update report status through the wrapper
def test_function_update_report_status(tmp_path, monkeypatch):
    reports_file = tmp_path / "reports.json"
    monkeypatch.setattr(data_manager, "DATA_FILE", reports_file)

    reports_file.write_text(json.dumps([
        {"case_id": "CASE-001", "status": "active"}
    ]), encoding="utf-8")

    result = data_manager.update_report_status(
        "CASE-001", "closed"
    )

    assert result is True

    saved = json.loads(reports_file.read_text(encoding="utf-8"))
    assert saved[0]["status"] == "closed"
    assert saved[0]["closed_date"] == date.today().isoformat()


# 14. Delete expired reports through the wrapper
def test_function_delete_expired_reports(tmp_path, monkeypatch):
    reports_file = tmp_path / "reports.json"
    image_directory = tmp_path / "images"

    monkeypatch.setattr(data_manager, "DATA_FILE", reports_file)
    monkeypatch.setattr(data_manager, "IMAGE_DIRECTORY", image_directory)

    old_date = (date.today() - timedelta(days=40)).isoformat()

    reports_file.write_text(json.dumps([
        {
            "case_id": "CASE-001",
            "status": "closed",
            "closed_date": old_date
        }
    ]), encoding="utf-8")

    result = data_manager.delete_expired_reports(30)

    assert result == 1
    assert json.loads(reports_file.read_text(encoding="utf-8")) == []


# 15. Clear temporary directory through the wrapper
def test_function_clear_temp_directory(tmp_path, monkeypatch, capsys):
    reports_file = tmp_path / "reports.json"
    monkeypatch.setattr(data_manager, "DATA_FILE", reports_file)

    temp_directory = tmp_path / "temp"
    temp_directory.mkdir()

    (temp_directory / "test.txt").write_text("temporary")

    result = data_manager.clear_temp_directory(temp_directory)

    captured = capsys.readouterr()

    assert result == 1
    assert list(temp_directory.iterdir()) == []
    assert "Cleared 1 temporary file(s)" in captured.out


# 16. Store image with invalid extension
def test_function_store_image_invalid_extension(tmp_path):
    source = tmp_path / "test.txt"
    source.write_text("not an image")

    result = data_manager.store_image(
        source, "CASE-001", tmp_path / "images"
    )

    assert result is None


# 17. Store image that does not exist
def test_function_store_image_missing_file(tmp_path):
    result = data_manager.store_image(
        tmp_path / "missing.jpg",
        "CASE-001",
        tmp_path / "images"
    )

    assert result is None


# 18. Store image in the configured image directory
def test_function_store_image_main_directory(tmp_path, monkeypatch):
    image_directory = tmp_path / "images"
    monkeypatch.setattr(data_manager, "IMAGE_DIRECTORY", image_directory)

    source = tmp_path / "source.JPG"
    source.write_bytes(b"image")

    result = data_manager.store_image(
        source, "CASE-001", image_directory
    )

    assert result == "CASE-001.jpg"
    assert (image_directory / "CASE-001.jpg").read_bytes() == b"image"


# 19. Handle image copy errors in the main directory
def test_function_store_image_copy_error(
    tmp_path, monkeypatch, capsys
):
    image_directory = tmp_path / "images"
    monkeypatch.setattr(data_manager, "IMAGE_DIRECTORY", image_directory)

    source = tmp_path / "source.jpg"
    source.write_bytes(b"image")

    def fake_copy(source, destination):
        raise OSError("Copy failed")

    monkeypatch.setattr(data_manager.shutil, "copy2", fake_copy)

    data_manager.store_image(source, "CASE-001", image_directory)

    captured = capsys.readouterr()
    assert "Error saving file to database:" in captured.out


# 20. Store image in temporary directory (non-container)
def test_function_store_image_temp_directory(tmp_path, monkeypatch):
    temp_directory = tmp_path / "temp"
    monkeypatch.setattr(data_manager, "TEMP_DIRECTORY", temp_directory)
    monkeypatch.delenv("APP_CONTAINER", raising=False)

    source = tmp_path / "source.jpg"
    source.write_bytes(b"image")

    result = data_manager.store_image(
        source, "CASE-001", temp_directory
    )

    if os.name == "nt":
        assert result == source.name
    else:
        assert result == str(source)
    assert (temp_directory / result).exists()


# 21. Handle duplicate image in temporary directory

def test_function_store_image_temp_same_file(
    tmp_path, monkeypatch, capsys
):
    temp_directory = tmp_path / "temp"
    temp_directory.mkdir()

    monkeypatch.setattr(
        data_manager, "TEMP_DIRECTORY", temp_directory
    )
    monkeypatch.delenv("APP_CONTAINER", raising=False)

    source = temp_directory / "source.jpg"
    source.write_bytes(b"image")

    def fake_copy(source, destination):
        raise shutil.SameFileError("Same file")

    monkeypatch.setattr(
        data_manager.shutil, "copy2", fake_copy
    )

    result = data_manager.store_image(
        source, "CASE-001", temp_directory
    )

    captured = capsys.readouterr()

    if os.name == "nt":
        assert result == source.name
    else:
        assert result == str(source)
    assert "File already exists" in captured.out

# 22. Handle copy error in temporary directory
def test_function_store_image_temp_copy_error(
    tmp_path, monkeypatch, capsys
):
    temp_directory = tmp_path / "temp"

    monkeypatch.setattr(data_manager, "TEMP_DIRECTORY", temp_directory)
    monkeypatch.delenv("APP_CONTAINER", raising=False)

    source = tmp_path / "source.jpg"
    source.write_bytes(b"image")

    def fake_copy(source, destination):
        raise OSError("Copy failed")

    monkeypatch.setattr(data_manager.shutil, "copy2", fake_copy)

    data_manager.store_image(source, "CASE-001", temp_directory)

    captured = capsys.readouterr()

    assert "Error copying file:" in captured.out


# 23. Store image in container environment
def test_function_store_image_container(tmp_path, monkeypatch):
    temp_directory = tmp_path / "temp"

    monkeypatch.setattr(data_manager, "TEMP_DIRECTORY", temp_directory)
    monkeypatch.setenv("APP_CONTAINER", "1")

    source = tmp_path / "source.jpg"
    source.write_bytes(b"image")

    result = data_manager.store_image(
        source, "CASE-001", temp_directory
    )

    assert result == "source.jpg"
    assert (temp_directory / result).exists()


# 24. Handle duplicate image in container environment
def test_function_store_image_container_same_file(
    tmp_path, monkeypatch, capsys
):
    temp_directory = tmp_path / "temp"
    temp_directory.mkdir()

    monkeypatch.setattr(
        data_manager, "TEMP_DIRECTORY", temp_directory
    )
    monkeypatch.setenv("APP_CONTAINER", "1")

    source = temp_directory / "source.jpg"
    source.write_bytes(b"image")

    def fake_copy(source, destination):
        raise shutil.SameFileError("Same file")

    monkeypatch.setattr(
        data_manager.shutil, "copy2", fake_copy
    )

    result = data_manager.store_image(
        source, "CASE-001", temp_directory
    )

    captured = capsys.readouterr()

    assert result == "source.jpg"
    assert "File already exists" in captured.out

# 25. Handle copy error in container environment
def test_function_store_image_container_copy_error(
    tmp_path, monkeypatch, capsys
):
    temp_directory = tmp_path / "temp"

    monkeypatch.setattr(data_manager, "TEMP_DIRECTORY", temp_directory)
    monkeypatch.setenv("APP_CONTAINER", "1")

    source = tmp_path / "source.jpg"
    source.write_bytes(b"image")

    def fake_copy(source, destination):
        raise OSError("Copy failed")

    monkeypatch.setattr(data_manager.shutil, "copy2", fake_copy)

    data_manager.store_image(source, "CASE-001", temp_directory)

    captured = capsys.readouterr()

    assert "Error copying file:" in captured.out