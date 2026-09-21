"""Persistent storage for report images and report metadata."""

import json
import shutil
from pathlib import Path
from typing import Mapping
from uuid import uuid4


PROJECT_DIRECTORY = Path(__file__).resolve().parent
IMAGE_DIRECTORY = PROJECT_DIRECTORY / "images"
REPORTS_FILE = PROJECT_DIRECTORY / "reports.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def store_image(
    source_path: str | Path,
    image_directory: Path = IMAGE_DIRECTORY,
) -> str:
    """Copy a JPG/JPEG/PNG into storage and return its generated filename."""
    source = Path(source_path).expanduser()
    if source.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError("Only JPG, JPEG, and PNG images can be stored.")
    if not source.is_file():
        raise FileNotFoundError(f"Image not found: {source}")

    image_directory.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}{source.suffix.lower()}"
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
    return reports


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
    stored_report["image_filename"] = store_image(source_path, image_directory)
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
    "load_reports",
    "save_report",
    "store_image",
]
