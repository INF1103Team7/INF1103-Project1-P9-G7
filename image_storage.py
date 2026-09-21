"""Persistent storage for report images and report metadata."""

import json
import shutil
from datetime import date
from pathlib import Path
from typing import Mapping
from uuid import uuid4


PROJECT_DIRECTORY = Path(__file__).resolve().parent
IMAGE_DIRECTORY = PROJECT_DIRECTORY / "images"
REPORTS_FILE = PROJECT_DIRECTORY / "reports.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def create_case_id() -> str:
	"""Create a readable unique identifier for a report."""
	return f"CASE-{date.today():%Y%m%d}-{uuid4().hex[:6].upper()}"


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


def load_reports(reports_file: Path = REPORTS_FILE) -> list[dict[str, object]]:
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


def save_report(
    report: Mapping[str, object],
    reports_file: Path = REPORTS_FILE,
    image_directory: Path = IMAGE_DIRECTORY,
) -> dict[str, object]:
    """Copy a report image and append the report with its stored filename."""
    source_path = report.get("image_path")
    if not isinstance(source_path, str):
        raise ValueError("The report must include an image_path.")

    stored_report = dict(report)
    case_id = str(stored_report.get("case_id") or create_case_id())
    stored_report["case_id"] = case_id
    stored_report["image_filename"] = store_image(
        source_path,
        case_id,
        image_directory,
    )
    del stored_report["image_path"]

    reports = load_reports(reports_file)
    reports.append(stored_report)
    reports_file.parent.mkdir(parents=True, exist_ok=True)
    with reports_file.open("w", encoding="utf-8") as file:
        json.dump(reports, file, indent=2)
    return stored_report


__all__ = [
    "IMAGE_DIRECTORY",
    "REPORTS_FILE",
    "create_case_id",
    "load_reports",
    "save_report",
    "store_image",
]
