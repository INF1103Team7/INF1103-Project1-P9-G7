"""Terminal input and output for the lost-and-found application."""

from datetime import date, datetime
from pathlib import Path
from typing import Callable, Iterable, Mapping

import image_storage


REPORT_TYPES = ("lost", "found")
CATEGORIES = (
	"student card",
	"bottle",
	"keys",
	"bag",
	"clothing",
	"electronics",
	"others",
)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]


def _read_non_empty(prompt: str, input_function: InputFunction) -> str:
	while True:
		value = input_function(prompt).strip()
		if value:
			return value
		print("Please enter a value.")


def _read_choice(
	prompt: str,
	choices: tuple[str, ...],
	input_function: InputFunction,
) -> str:
	while True:
		value = input_function(prompt).strip().lower()
		if value.isdigit() and 1 <= int(value) <= len(choices):
			return choices[int(value) - 1]
		if value in choices:
			return value
		print(f"Please choose one of: {', '.join(choices)}.")


def _read_date(input_function: InputFunction) -> str:
	while True:
		value = _read_non_empty("Date of loss/finding (DD-MM-YYYY): ", input_function)
		try:
			occurrence_date = datetime.strptime(value, "%d-%m-%Y").date()
		except ValueError:
			print("Please use a valid date in DD-MM-YYYY format.")
			continue
		if occurrence_date > date.today():
			print("The date cannot be in the future.")
			continue
		return value


def _read_image_path(input_function: InputFunction) -> str:
	while True:
		value = _read_non_empty("Image path (JPG, JPEG, or PNG): ", input_function)
		image_path = Path(value).expanduser()
		if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
			print("Please submit an image with a .jpg, .jpeg, or .png extension.")
			continue
		if not image_path.is_file():
			print("That image file could not be found. Please check the path.")
			continue
		return str(image_path)


def _print_choices(title: str, choices: tuple[str, ...]) -> None:
	print(title)
	for number, choice in enumerate(choices, start=1):
		print(f"{number}. {choice.title()}")


def collect_report(input_function: InputFunction = input) -> dict[str, str]:
	"""Collect and validate one lost or found report from the terminal."""
	_print_choices("Report type:", REPORT_TYPES)
	report_type = _read_choice("Select report type: ", REPORT_TYPES, input_function)

	_print_choices("Item category:", CATEGORIES)
	category = _read_choice("Select item category: ", CATEGORIES, input_function)

	return {
		"report_type": report_type,
		"category": category,
		"description": _read_non_empty("Item description: ", input_function),
		"image_path": _read_image_path(input_function),
		"date": _read_date(input_function),
	}


def format_record(record: Mapping[str, object]) -> str:
	"""Return one report in a consistent human-readable format."""
	report_type = str(record.get("report_type", record.get("type", "unknown"))).title()
	category = str(record.get("category", "unknown")).title()
	description = str(record.get("description", "No description"))
	image_path = str(
		record.get(
			"image_filename",
			record.get("image_path", record.get("image", "No image")),
		)
	)
	occurrence_date = str(record.get("date", record.get("occurrence_date", "Unknown date")))
	report_id = record.get("report_id")
	identifier = f" [{report_id}]" if report_id is not None else ""
	return (
		f"{report_type} report{identifier}\n"
		f"  Category: {category}\n"
		f"  Description: {description}\n"
		f"  Date: {occurrence_date}\n"
		f"  Image: {image_path}"
	)


def format_records(records: Iterable[Mapping[str, object]]) -> str:
	"""Return a numbered list of reports, or a useful empty-state message."""
	record_list = list(records)
	if not record_list:
		return "No reports found."
	return "\n\n".join(
		f"{number}. {format_record(record)}"
		for number, record in enumerate(record_list, start=1)
	)


def display_summary(records: Iterable[Mapping[str, object]]) -> None:
	"""Print the summary view for the supplied reports."""
	print("\nLost-and-Found Summary")
	print("======================")
	print(format_records(records))


def collect_summary_view(
	records: Iterable[Mapping[str, object]],
	input_function: InputFunction = input,
) -> bool:
	"""Handle the ``/summary`` command and return whether it was requested."""
	command = input_function("Enter /summary to view reports, or press Enter to continue: ").strip().lower()
	if command == "/summary":
		display_summary(records)
		return True
	return False


def run_cli(input_function: InputFunction = input) -> None:
	"""Run the terminal workflow for creating and viewing reports."""
	try:
		reports = image_storage.load_reports()
	except (OSError, ValueError) as error:
		reports = []
		print(f"Could not load saved reports: {error}")
	while True:
		print("\nLost-and-Found System")
		print("1. Submit a report")
		print("2. View /summary")
		print("3. Exit")
		command = input_function("Select an option: ").strip().lower()

		if command in {"1", "report", "submit"}:
			report = collect_report(input_function)
			try:
				reports.append(image_storage.save_report(report))
			except (OSError, ValueError) as error:
				print(f"Could not save report: {error}")
			else:
				print("Report submitted successfully.")
		elif command in {"2", "/summary", "summary"}:
			display_summary(reports)
		elif command in {"3", "exit", "quit", "q"}:
			print("Goodbye.")
			return
		else:
			print("Please choose 1, 2, or 3.")


__all__ = [
	"CATEGORIES",
	"REPORT_TYPES",
	"collect_report",
	"collect_summary_view",
	"display_summary",
	"format_record",
	"format_records",
	"run_cli",
]


if __name__ == "__main__":
	run_cli()
