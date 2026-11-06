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
from io_classes import (
    Bag,
    Bottle,
    CATEGORIES,
    Clothing,
    Electronics,
    Format,
    Keys,
    OtherItem,
    Items,
    PrintMenu,
    StudentCard,
)

# Constants
REPORT_TYPES = ("lost", "found")
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
		PrintMenu.write("Please enter a value.")

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
		PrintMenu.write(f"Please choose one of: {', '.join(choices)}.")

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
			PrintMenu.write("Please use a valid date in DD-MM-YYYY format.")
			continue
		if occurrence_date > date.today():
			PrintMenu.write("The date cannot be in the future.")
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
					PrintMenu.write("Image selection is cancelled.")
					return None

				image_path = Path(file_path)

				if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
					PrintMenu.write("Please submit an image with a .jpg, .jpeg, or .png extension.")
					continue

				if not image_path.is_file():
					PrintMenu.write("The image file could not be found. Please try again.")
					continue

				PrintMenu.write("The image is added successfully. \n")

				return str(image_path)
			except (tk.TclError, Exception) as e:
				PrintMenu.write(f"[!] An error occurred while selecting the image: {e}")
				pass
	# CLI fallback if container does not have GUI support
	PrintMenu.write("\n[!] Headless container environment detected. Using CLI input.")
	while True:
		PrintMenu.write("Please enter the full path to the image file.")
		_print_nav()
		cli_input = input_function("Enter the image name make sure the image is stored in the /temp directory (Example: image.jpg): ")
		
		if cli_input.lower() == "b":
			return BACK
		elif cli_input.lower() == "m":
			return MAIN

		image_path = Path("temp/" + cli_input).expanduser()

		if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
			PrintMenu.write("Please submit an image with a .jpg, .jpeg, or .png extension.\n")
			continue

		if not image_path.is_file():
			PrintMenu.write("The image file could not be found. Please try again.\n")
			continue

		PrintMenu.write("The image is added successfully.\n")
		return str(image_path)

# Helper function to print menu choices for the user to select from
def _print_choices(title: str, choices: tuple[str, ...]) -> None:
	"""_summary_
		Function to print menu choices for the user to select from.
	Args:
		title (str): Title of the menu
		choices (tuple[str, ...]): Tuple containing the choices to display
	"""
	PrintMenu.choices(title, choices)

# Helper function to print navigation options for the user to go back or return to the main menu
def _print_nav(include_back: bool = True) -> None:
	"""_summary_
		Function to print navigation options for the user to go back or return to the main menu.
	Args:
		include_back (bool, optional): Whether to display back option or not. Defaults to True.
	"""
	PrintMenu.navigation(include_back)

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
	category: Items | None = None
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

			selected_category = _read_choice(
				"Select item category: ", CATEGORIES, input_function
			)

			if selected_category == MAIN:
				return None

			if selected_category == BACK:
				stage = 1
				continue 

			category = Items.from_value(selected_category)
			stage = 3

		#Stage 3 - Description 
		elif stage == 3:

			PrintMenu.write(
				f"\nEnter item description ({category.description_guidance})."
			)
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

			PrintMenu.write("\nEnter the date of loss/finding.")
			_print_nav()

			date = _read_date(input_function)

			if date == MAIN:
				return None 

			if date == BACK:
				stage = 4
				continue

			return {
				"report_type": report_type,
				"category": category.value,
				"description": description,
				"image_path": image_path,
				"date": date,
			}

# Function to format a single report in a consistent human-readable format
def format_record(record: Mapping[str, object]) -> str:
	return Format.record(record)

# Function to receive a list of reports to format for summary display
def format_records(records: Iterable[Mapping[str, object]]) -> str:
	return Format.records(records)

# Function to display a summary of reports in a human-readable format
def display_summary(records: Iterable[Mapping[str, object]]) -> None:
	PrintMenu.display_summary(records)

# Function to return the best match report to the user and ask for confirmation if it is a match
def resolve_best_match(best_match, input_function: InputFunction = input):
	return PrintMenu.confirm_best_match(best_match, input_function)

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
		PrintMenu.section(
			"Welcome to the AI powered lost and found system!",
			50,
		)
		PrintMenu.write("1. Submit a lost/found report")
		PrintMenu.write("2. View summary of all reports")
		PrintMenu.write("3. Exit")
		command = input_function("Select an option: ").strip().lower()

		if command in {"1", "report", "submit"}:
			report = collect_report(input_function)

			if report is None: 
				PrintMenu.write("\nReport submission cancelled.")
				continue 

			PrintMenu.section("Report submitted successfully!", 32)

			return report
		elif command in {"2", "/summary", "summary"}:
			try:
				report_list = data_manager.load_reports()
			except (OSError, ValueError) as error:
				report_list = []
				PrintMenu.write(f"Could not load saved reports: {error}")
			display_summary(report_list)

		elif command in {"3", "exit", "quit", "q"}:
			PrintMenu.write("\nExiting the AI powered lost and found system. Goodbye!")
			return "quit"
		else:
			PrintMenu.write("Please choose 1, 2, or 3.")

# Import control
__all__ = [
	"Bag",
	"Bottle",
	"CATEGORIES",
	"Clothing",
	"Electronics",
	"Format",
	"Items",
	"Keys",
	"OtherItem",
	"PrintMenu",
	"REPORT_TYPES",
	"StudentCard",
	"collect_report",
	"display_summary",
	"format_record",
	"format_records",
	"resolve_best_match",
	"run_cli",
]

if __name__ == "__main__":
	run_cli()
