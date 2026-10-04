# imports
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
DATA_FILE = PROJECT_DIRECTORY / "reports.json"

# set the location of the image storage directory
IMAGE_DIRECTORY = PROJECT_DIRECTORY / "images"

# valid image file extensions that can be stored
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# valid statues that a report can have
VALID_STATUSES = [
    "active",
    "claimed",
    "returned",
    "closed"
]

def _migrate_old_image_names(
    reports: list[dict[str, object]],
    image_directory: Path,
) -> bool:
    """Rename images from older records that do not have case IDs."""
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

def create_case_id() -> str:
	"""Create a readable unique identifier for a report."""
	return f"CASE-{date.today():%Y%m%d}-{uuid4().hex[:6].upper()}"

# loads all existing reports from reports.json
def load_reports(reports_file: Path = DATA_FILE) -> list[dict[str, object]]:
    """Load saved reports, returning an empty list when none exist yet."""
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

# saves the current lists of reports into to reports.json
# def save_reports(reports):
#     try:
#         # opens reports.json in write mode
#         with DATA_FILE.open("w", encoding="utf-8") as file:
#             # save the report list as formatted JSON
#             json.dump(reports, file, indent=4)
#         # return true when the reports are saved successfully
#         return True
#     # return false if the file cannot be written
#     except OSError:
#         return False

def save_reports(
    report: Mapping[str, object],
    reports_file: Path = DATA_FILE,
    image_directory: Path = IMAGE_DIRECTORY,
) -> dict[str, object]:
    """Copy a report image and append the report with its stored filename."""
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

def store_image(
    source_path: str | Path,
    case_id: str,
    image_directory: Path = IMAGE_DIRECTORY,
) -> str:
    """Copy an image into storage using the case ID as its filename."""
    source = Path(source_path).expanduser()
    if source.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError("Only JPG, JPEG, and PNG images can be stored.")
    if not source.is_file():
        raise FileNotFoundError(f"Image not found: {source}")

    image_directory.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{case_id}{source.suffix.lower()}"
    shutil.copy2(source, image_directory / stored_filename)
    return stored_filename

# Add a new report and prevent duplicate case IDs
# def add_report(report):

#     reports = load_reports()
#     stored_report = dict(report)

#     # Generate a unique case ID if one does not exist
#     case_id = stored_report.get("case_id")

#     if not case_id:
#         case_id = create_case_id()
#         stored_report["case_id"] = case_id

#     # Prevent duplicate reports
#     for existing_report in reports:
#         if existing_report.get("case_id") == case_id:
#             return False

#     # New reports are active by default
#     if "status" not in stored_report:
#         stored_report["status"] = "active"

#     reports.append(stored_report)

#     return save_reports(reports)

# Find a specific report using its case ID
def get_report_by_id(case_id):
    reports = load_reports()

    for report in reports:
        if report.get("case_id") == case_id:
            return report

    return None

# Filter reports by category
def get_reports_by_category(report_category):
    reports = load_reports()

    matching_reports = []

    for report in reports:
        if report.get("category") == report_category:
            matching_reports.append(report)

    return matching_reports

# Return only reports that are currently active
def get_active_reports():
    reports = load_reports()

    active_reports = []

    for report in reports:
        if report.get("status") == "active":
            active_reports.append(report)

    return active_reports

# Update a report's status and record when it is closed
def update_report_status(case_id, new_status):

    if new_status not in VALID_STATUSES:
        return False

    reports = load_reports()
    for report in reports:
        if report.get("case_id") == case_id:
            report["status"] = new_status

            # Store the closure date for automatic deletion later
            if new_status == "closed":
                report["closed_date"] = date.today().isoformat()
            return save_reports(reports)
    return False

# Delete reports that have been closed longer than the retention period (30 days)
def delete_expired_reports(retention_days=30):
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
                    continue

            except ValueError:
                pass

        remaining_reports.append(report)
    # Only update the file when a report has been deleted
    if deleted_count > 0:
        save_reports(remaining_reports)

    return deleted_count

# Import controls
__all__ = [
    "IMAGE_DIRECTORY",
    "DATA_FILE",
    "create_case_id",
    "load_reports",
    "save_reports",
    "store_image",
    "get_report_by_id",
    "get_reports_by_category",
    "get_active_reports",
    "update_report_status",
    "delete_expired_reports"
]
