# data_manager file to handle all data storage and retrieval operations for the lost and found reports

# Imports
import json
import shutil
from typing import Mapping
from uuid import uuid4
from pathlib import Path
from datetime import date, datetime, timedelta

# Constants
# location of the JSON file used to store all lost and found reports
PROJECT_DIRECTORY = Path(__file__).resolve().parent

# set the location of the JSON file used to store reports
DATA_FILE = PROJECT_DIRECTORY / "found_reports.json"

# set the location of the image storage directory
IMAGE_DIRECTORY = PROJECT_DIRECTORY / "images"

# set the location of the temporary storage directory for extraction
TEMP_DIRECTORY = PROJECT_DIRECTORY / "temp"

# valid image file extensions that can be stored
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# valid statues that a report can have
VALID_STATUSES = [
    "active",
    "closed"
]

# Functions
# Migrate old image names to new format with case IDs (if any)
def _migrate_old_image_names(
    reports: list[dict[str, object]],
    image_directory: Path,
) -> bool:
    """_summary_
        Function to migrate old image names to new format with case IDs
    Args:
        reports (list[dict[str, object]]): List of reports to be checked for old image names
        image_directory (Path): Path to the image directory where the images are stored

    Returns:
        bool: True if any image names were migrated, False otherwise
    """
    changed = False
    for report in reports:
        if report.get("case_id"):
            continue
        old_filename = report.get("image_filename")
        if not isinstance(old_filename, str):
            continue

        case_id = create_case_id()
        old_image = image_directory / old_filename
        new_filename = f"{case_id}{Path(old_filename).suffix.lower()}"
        new_image = image_directory / new_filename
        if old_image.is_file():
            old_image.rename(new_image)
            report["image_filename"] = new_filename
            report["case_id"] = case_id
            changed = True
    return changed

# Create a unique case ID for each report
def create_case_id() -> str:
    """_summary_
        Function to create a unique case ID for each report
    Returns:
        str: The unique case ID for the report.
    """
    return f"CASE-{date.today():%Y%m%d}-{uuid4().hex[:6].upper()}"

# loads all existing reports from reports.json
def load_reports(reports_file: Path = DATA_FILE) -> list[dict[str, object]]:
    """_summary_
        Function to load all existing reports from found_reports.json
    Args:
        reports_file (Path, optional): The path to the reports file. Defaults to DATA_FILE.

    Raises:
        ValueError: If the reports file does not contain a list.

    Returns:
        list[dict[str, object]]: A list of dictionaries representing the reports loaded from the reports file.
    """
    if not reports_file.is_file():
        return []
    with reports_file.open("r", encoding="utf-8") as file:
        reports = json.load(file)
    if not isinstance(reports, list):
        raise ValueError("The reports file must contain a list.")
    if _migrate_old_image_names(reports, reports_file.parent / "images"):
        with reports_file.open("w", encoding="utf-8") as file:
            json.dump(reports, file, indent=2)
    return reports

# Save new reports to found_reports.json
def save_new_reports(
    report: Mapping[str, object],
    reports_file: Path = DATA_FILE,
    image_directory: Path = IMAGE_DIRECTORY,
) -> dict[str, object]:
    """_summary_
        Function to save new reports to found_reports.json
    Args:
        report (Mapping[str, object]): The report data to be saved.
        reports_file (Path, optional): The path to the reports file. Defaults to DATA_FILE.
        image_directory (Path, optional): The path to the image directory. Defaults to IMAGE_DIRECTORY.

    Raises:
        ValueError: If the report does not include an image_path or if the image_path is not a string.

    Returns:
        dict[str, object]: The saved report data.
    """
    source_path = report.get("image_path")
    if source_path  is not None and not isinstance(source_path, str):
        raise ValueError("The report must include an image_path.")

    stored_report = dict(report)
    case_id = str(stored_report.get("case_id") or create_case_id())
    stored_report["case_id"] = case_id
    if isinstance(source_path, str):
        stored_report["image_filename"] = store_image(
            source_path,
            case_id,
            image_directory,
        )
    stored_report.pop("image_path", None)

    # New reports are active by default
    if "status" not in stored_report:
        stored_report["status"] = "active"

    reports = load_reports(reports_file)
    reports.append(stored_report)
    reports_file.parent.mkdir(parents=True, exist_ok=True)
    with reports_file.open("w", encoding="utf-8") as file:
        json.dump(reports, file, indent=2)
    return stored_report

# saves the current lists of reports into to found_reports.json
def save_report_list(reports):
    """_summary_
        Function to save the current list of reports into the found_reports.json file.
    Args:
        reports (list): The list of reports to be saved into the found_reports.json file.

    Returns:
        bool: True if the reports are saved successfully, False otherwise.
    """
    try:
        # opens reports.json in write mode
        with DATA_FILE.open("w", encoding="utf-8") as file:
            # save the report list as formatted JSON
            json.dump(reports, file, indent=4)
        # return true when the reports are saved successfully
        return True
    # return false if the file cannot be written
    except OSError:
        return False

# Store an image in the images directory
def store_image(
    source_path: str | Path,
    case_id: str,
    image_directory
) -> str:
    """_summary_
        Function to store an image in the images directory with a new filename based on the case ID.
    Args:
        source_path (str | Path): The path to the source image file to be stored.
        case_id (str): The case ID to be used for the new image filename.
        image_directory (Path, optional): The path to the image directory. Defaults to IMAGE_DIRECTORY.

    Raises:
        ValueError: If the source path is not a valid image file or if the case ID is not a string.
        FileNotFoundError: If the source image file is not found.

    Returns:
        str: The filename of the stored image.
    """
    image_directory = Path(image_directory)
    source = Path(source_path).expanduser()
    if source.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError("Only JPG, JPEG, and PNG images can be stored.")
    if not source.is_file():
        raise FileNotFoundError(f"Image not found: {source}")

    image_directory.mkdir(parents=True, exist_ok=True)
    if image_directory == IMAGE_DIRECTORY:
        stored_filename = f"{case_id}{source.suffix.lower()}"
        shutil.copy2(source, image_directory / stored_filename)
    elif image_directory == TEMP_DIRECTORY:
        stored_filename = f"{str(source).split("\\")[-1]}"
        shutil.copy2(source, image_directory / stored_filename)
    return stored_filename

# Filter reports by category
def get_reports_by_category(report_category):
    """_summary_
        Function to filter reports by category.
    Args:
        report_category (str): The category of reports to be filtered.

    Returns:
        list: A list of reports that match the specified category.
    """
    reports = get_active_reports()

    matching_reports = []

    for report in reports:
        if report.get("category") == report_category:
            matching_reports.append(report)

    return matching_reports

# Return only reports that are currently active
def get_active_reports():
    """_summary_
        Function to return only reports that are currently active.
    Returns:
        list: list: A list of active reports.
    """
    reports = load_reports()

    active_reports = []

    for report in reports:
        if report.get("status") == "active":
            active_reports.append(report)

    return active_reports

# Update a report's status and record when it is closed
def update_report_status(case_id, new_status):
    """_summary_
        Function to update a report's status and record when it is closed.
    Args:
        case_id (str): Case ID of the report to be updated
        new_status (str): New status to be set for the report

    Returns:
        bool: True if the report was updated successfully, False otherwise
    """
    new_status = new_status.lower()
    if new_status not in VALID_STATUSES:
        return False

    reports = load_reports()
    for report in reports:
        if report.get("case_id") == case_id:
            report["status"] = new_status

            # Store the closure date for automatic deletion later
            if new_status == "closed":
                report["closed_date"] = date.today().isoformat()
            return save_report_list(reports)
    return False

# Delete reports that have been closed longer than the retention period (30 days)
def delete_expired_reports(retention_days=30):
    """_summary_
        Function to delete reports that have been closed longer than the retention period (30 days).
    Args:
        retention_days (int, optional): The number of days to retain closed reports before deletion. Defaults to 30.

    Returns:
        int: The number of reports deleted from the database.
    """
    reports = load_reports()
    remaining_reports = []
    deleted_count = 0
    
    # Calculate the expiry date based on the retention period
    expiry_date = date.today() - timedelta(days=retention_days)

    for report in reports:
        if report.get("status") == "closed" and report.get("closed_date"):
            try:
                closed_date = datetime.strptime(
                    report["closed_date"],
                    "%Y-%m-%d"
                ).date()
                # Remove reports that have expired
                if closed_date <= expiry_date:
                    deleted_count += 1
                    try:
                        file_to_delete = IMAGE_DIRECTORY / report.get("image_filename")
                        if file_to_delete.is_file():
                            file_to_delete.unlink()
                        print(f"[+] Deleted image for report with case ID: {report.get('case_id')}")
                    except TypeError:
                        print(f"[!] No image filename found for report with case ID: {report.get('case_id')}. Skipping image deletion.")
                    except PermissionError:
                        print(f"[!] Permission denied when trying to delete image for report with case ID: {report.get('case_id')}. Skipping image deletion.")
                    continue
            except ValueError:
                pass

        remaining_reports.append(report)
    # Only update the file when a report has been deleted
    if deleted_count > 0:
        save_report_list(remaining_reports)

    return deleted_count

# Import controls
__all__ = [
    "IMAGE_DIRECTORY",
    "DATA_FILE",
    "create_case_id",
    "load_reports",
    "save_new_reports",
    "save_report_list",
    "store_image",
    "get_reports_by_category",
    "get_active_reports",
    "update_report_status",
    "delete_expired_reports"
]
