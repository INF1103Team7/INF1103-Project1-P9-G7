# io_manager file for application CLI interface

# Imports
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Iterable, Mapping
import tkinter as tk
from tkinter import filedialog
import os
import data_manager
from dotenv import load_dotenv

# Constants
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
BACK = "BACK"
MAIN = "MAIN"

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]

# Functions
# Helper functions to read user input with non empty validation and navigation options
def _read_non_empty(prompt: str, input_function: InputFunction) -> str:
	"""_summary_
		Function to read input from the user and ensure that it is not empty. 
		The function will keep prompting the user until a non-empty value is provided or the user chooses to go back or return to the main menu.
	Args:
		prompt (str): Prompt to display to the user
		input_function (InputFunction): A callable function to read user input. Defaults to the built-in input function.

	Returns:
		str: The non-empty input value provided by the user, or BACK/MAIN if the user chooses to go back or return to the main menu.
	"""
	while True:
		value = input_function(prompt).strip()

		if value.lower() == "b":
			return BACK

		if value.lower() == "m":
			return MAIN
		
		if value:
			return value
		print("Please enter a value.")

# Helper functions to read user input with choice validation and navigation options
def _read_choice(
	prompt: str,
	choices: tuple[str, ...],
	input_function: InputFunction,
) -> str:
	"""_summary_
		Function to read a choice from the user based on a list of available options.
	Args:
		prompt (str): Prompt to display to the user
		choices (tuple[str, ...]): Tuple of available choices for the user to select from
		input_function (InputFunction): A callable function to read user input. Defaults to the built-in input function.

	Returns:
		str: The selected choice from the available options, or BACK/MAIN if the user chooses to go back or return to the main menu.
	"""
	while True:
		value = input_function(prompt).strip().lower()

		if value == "b":
			return BACK
		
		if value == "m":
			return MAIN
		
		if value.isdigit() and 1 <= int(value) <= len(choices):
			return choices[int(value) - 1]
		
		if value in choices:
			return value
		print(f"Please choose one of: {', '.join(choices)}.")

# Helper function to read date input from the user with validation and navigation options
def _read_date(input_function: InputFunction) -> str:
	"""_summary_
		Function to read input from the user and return a date string in DD-MM-YYYY format after validating the input.
	Args:
		input_function (InputFunction): A callable function to read user input. Defaults to the built-in input function.

	Returns:
		str: date in DD-MM-YYYY format
	"""
	while True:
		value = _read_non_empty("\nDate of loss/finding (DD-MM-YYYY): ", input_function)

		if value == BACK:
			return  BACK

		if value == MAIN:
			return MAIN
		
		try:
			occurrence_date = datetime.strptime(value, "%d-%m-%Y").date()
		except ValueError:
			print("Please use a valid date in DD-MM-YYYY format.")
			continue
		if occurrence_date > date.today():
			print("The date cannot be in the future.")
			continue

		return value

# Helper function to read image path input from the user with validation and navigation options
def _read_image_path(input_function: InputFunction) -> str:
	"""_summary_
		Function to read the image path from the user using a file dialog. Validates the file extension and existence of the file.
	Args:
		input_function (InputFunction): A callable function to read user input. Defaults to the built-in input function.

	Returns:
		str: The path to the selected image file, or None if the selection is cancelled.
	"""
	# Load environment variables from .env file
	load_dotenv()
	print(os.environ.get("APP_CONTAINER"))
	if os.environ.get("APP_CONTAINER") != "1":
		while True: 
			try:
				root = tk.Tk()
				root.withdraw()

				file_path = filedialog.askopenfilename(
					title = "Select an image",
					filetypes = [
						("Image files", "*jpg *jpeg *png"),
						("JPG files","*jpg"),
						("JPEG files", "*jpeg"),
						("PNG files", "*png"),
					],
				)

				root.destroy()

				if not file_path:
					print("Image selection is cancelled.")
					return None

				image_path = Path(file_path)

				if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
					print("Please submit an image with a .jpg, .jpeg, or .png extension.")
					continue

				if not image_path.is_file():
					print("The image file could not be found. Please try again.")
					continue

				print("The image is added successfully. \n")

				return str(image_path)
			except (tk.TclError, Exception) as e:
				print(f"[!] An error occurred while selecting the image: {e}")
				pass
	# CLI fallback if container does not have GUI support
	print("\n[!] Headless container environment detected. Using CLI input.")
	while True:
		print("Please enter the full path to the image file.")
		_print_nav()
		cli_input = input_function("Enter the image name make sure the image is stored in the /temp directory (Example: image.jpg): ")
		
		if cli_input.lower() == "b":
			return BACK
		elif cli_input.lower() == "m":
			return MAIN

		image_path = Path("temp/" + cli_input).expanduser()

		if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
			print("Please submit an image with a .jpg, .jpeg, or .png extension.\n")
			continue

		if not image_path.is_file():
			print("The image file could not be found. Please try again.\n")
			continue

		print("The image is added successfully.\n")
		return str(image_path)

# Helper function to print menu choices for the user to select from
def _print_choices(title: str, choices: tuple[str, ...]) -> None:
	"""_summary_
		Function to print menu choices for the user to select from.
	Args:
		title (str): Title of the menu
		choices (tuple[str, ...]): Tuple containing the choices to display
	"""
	print(title)
	for number, choice in enumerate(choices, start=1):
		print(f"{number}. {choice.title()}")

# Helper function to print navigation options for the user to go back or return to the main menu
def _print_nav(include_back: bool = True) -> None:
	"""_summary_
		Function to print navigation options for the user to go back or return to the main menu.
	Args:
		include_back (bool, optional): Whether to display back option or not. Defaults to True.
	"""
	if include_back:
		print("B. Go back to the previous step.")

	print("M. Go back to the Main Menu")

# Function to craft report based on user input
def collect_report(input_function: InputFunction = input) -> dict[str, str]:
	"""_summary_
		Function to collect a lost/found report from the user through a series of prompts. 
		The function guides the user through multiple stages to gather necessary information for the report.
	Args:
		input_function (InputFunction, optional): A callable function to read user input. Defaults to the built-in input function.

	Returns:
		dict[str, str]: Dictionary of string values or None
	"""

	stage = 1

	report_type = None
	category = None
	description = None
	image_path = None
	date = None

	while True:

		#Stage 1 - Report Type
		if stage == 1:

			_print_choices("\nReport type:", REPORT_TYPES)
			_print_nav(include_back=False)

			report_type = _read_choice("Select report type: ", REPORT_TYPES, input_function)

			if report_type == MAIN:
				return None

			stage = 2

		#Stage 2 - Category
		elif stage == 2:

			_print_choices("\nItem category:", CATEGORIES)
			_print_nav()

			category = _read_choice("Select item category: ", CATEGORIES, input_function)

			if category == MAIN:
				return None

			if category == BACK:
				stage = 1
				continue 

			stage = 3

		#Stage 3 - Description 
		elif stage == 3:

			print("\nEnter item description. ")
			_print_nav()

			description = _read_non_empty("\nItem description: ", input_function)

			if description == MAIN:
				return None 

			if description == BACK:
				stage = 2
				continue

			stage = 4

		#Stage 4 - Image Upload
		elif stage == 4:

			_print_choices("\nWould you like to upload an image?", ("yes","no"))
			_print_nav()

			upload_image = _read_choice("Select an option: ", ("yes", "no"), input_function)

			if upload_image == MAIN:
				return None

			if upload_image == BACK:
				stage = 3
				continue

			image_path = None 
			if upload_image == "yes":
				image_path = _read_image_path(input_function)

				if image_path is BACK:
					continue
				if image_path == MAIN:
					break
			stage = 5

		#Stage 5 - Date
		elif stage == 5:

			print("\nEnter the date of loss/finding.")
			_print_nav()

			date = _read_date(input_function)

			if date == MAIN:
				return None 

			if date == BACK:
				stage = 4
				continue

			return {
				"report_type": report_type,
				"category": category,
				"description": description,
				"image_path": image_path,
				"date": date,
			}

# Function to format a single report in a consistent human-readable format
def format_record(record: Mapping[str, object]) -> str:
	"""_summary_
		Function that receives a single report from database and formats it in a consistent human-readable format for summary display
	Args:
		record (Mapping[str, object]): A single report from the database represented as a mapping of string keys to object values.

	Returns:
		str: A formatted string representing the report in a human-readable format.
	"""
	report_type = str(record.get("report_type", record.get("type", "unknown"))).title()
	case_id = str(record.get("case_id", "unknown"))
	status = str(record.get('status', 'Unknown'))
	category = str(record.get("category", "unknown")).title()
	identifying_features = record.get("identifying_features", "No identifying features")
	image_path = str(
		record.get(
			"image_filename",
			record.get("image_path", record.get("image", "No image")),
		)
	)
	occurrence_date = str(record.get("date", record.get("occurrence_date", "Unknown date")))
	return (
		f"{report_type} report\n"
		f"  Case ID: {case_id}\n"
		f"  Status: {status}\n"
		f"  Category: {category}\n"
		f"  Identifying Features: {', '.join(identifying_features) if isinstance(identifying_features, list) else identifying_features}\n"
		f"  Date: {occurrence_date}\n"
		f"  Image: {image_path}"
	)

# Function to receive a list of reports to format for summary display
def format_records(records: Iterable[Mapping[str, object]]) -> str:
	"""_summary_
		Function that receives a list of reports from database and formats them in a consistent human-readable format for summary display
	Args:
		records (Iterable[Mapping[str, object]]): An iterable of reports from the database, where each report is represented as a mapping of string keys to object values.

	Returns:
		str: A formatted string representing the list of reports in a human-readable format, with each report separated by two newlines.
	"""
	record_list = list(records)
	if not record_list:
		return "No reports found."
	return "\n\n".join(
		f"{number}. {format_record(record)}"
		for number, record in enumerate(record_list, start=1)
	)

# Function to display a summary of reports in a human-readable format
def display_summary(records: Iterable[Mapping[str, object]]) -> None:
	"""_summary_
		Function that receives a list of reports from database and displays them in a consistent human-readable format for summary display
	Args:
		records (Iterable[Mapping[str, object]]): An iterable of reports from the database, where each report is represented as a mapping of string keys to object values.
	"""
	print("\nLost-and-Found Summary")
	print("======================")
	print(format_records(records))

# Function to return the best match report to the user and ask for confirmation if it is a match
def resolve_best_match(best_match, input_function: InputFunction = input):
	"""_summary_
		Function to return the best match report to the user and ask for confirmation if it is a match.
	Args:
		best_match (dict): The best match report to be presented to the user.
		input_function (InputFunction, optional): A callable function to read user input. Defaults to the built-in input function.

	Returns:
		boolean: True if the user confirms the match, False otherwise.
	"""
	print("[+] Best match found from database:")
	evaluation = best_match.get("evaluation")
	print(f"Verdict: {evaluation.get("status")}")
	print(f"Final score after applying business rules: {evaluation.get("final_composite_score")}/100")
	print(f"Matched rules: {', '.join(evaluation.get("matched_rules_list")) if evaluation.get("matched_rules_list") else 'None'}")
	print(f"Mismatched rules: {', '.join(evaluation.get("mismatched_rules_list")) if evaluation.get("mismatched_rules_list") else 'None'}")
	print(f"Summary: {evaluation.get("evaluation_summary")}")

	while True:
		resolve = input_function("Is this a match for the item you have lost? (yes/no): ").strip().lower()

		if resolve in {"yes", "y"}:
			return True
		elif resolve in {"no", "n"}:
			return False
		else:
			print("Please enter 'yes' or 'no'.")

# Function to run the main command-line interface for the AI powered lost and found system
def run_cli(input_function: InputFunction = input):
	"""_summary_
		Runs the command-line interface for the AI powered lost and found system.
	Args:
		input_function (InputFunction, optional): A callable function to read user input. Defaults to the built-in input function.

	Returns:
		dict / str: Dictionary of information about the report submitted by user / string "quit" if user chooses to exit the program
	"""
	while True:
		print("\n" + "=" * 50)
		print("Welcome to the AI powered lost and found system!")
		print("=" * 50)
		print("1. Submit a lost/found report")
		print("2. View summary of all reports")
		print("3. Exit")
		command = input_function("Select an option: ").strip().lower()

		if command in {"1", "report", "submit"}:
			report = collect_report(input_function)

			if report is None: 
				print("\nReport submission cancelled.")
				continue 

			print("\n" + "=" * 32)
			print("Report submitted successfully!")
			print("=" * 32)

			return report
		elif command in {"2", "/summary", "summary"}:
			try:
				report_list = data_manager.load_reports()
			except (OSError, ValueError) as error:
				report_list = []
				print(f"Could not load saved reports: {error}")
			display_summary(report_list)

		elif command in {"3", "exit", "quit", "q"}:
			print("\nExiting the AI powered lost and found system. Goodbye!")
			return "quit"
		else:
			print("Please choose 1, 2, or 3.")

# Import control
__all__ = [
	"CATEGORIES",
	"REPORT_TYPES",
	"collect_report",
	"display_summary",
	"format_record",
	"format_records",
	"resolve_best_match",
	"run_cli",
]

if __name__ == "__main__":
	run_cli()
