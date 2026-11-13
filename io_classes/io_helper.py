# io helper class to handle user input and output for the lost-and-found application

# Imports
import os
import tkinter as tk
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from tkinter import filedialog

from dotenv import load_dotenv

from .print_menu import PrintMenu

InputFunction = Callable[[str], str]

# Helper class to handle user input and output for the lost-and-found application
class IoHelper:
    BACK = "BACK"
    MAIN = "MAIN"
    IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

    @staticmethod
    def read_non_empty(prompt: str, input_function: InputFunction) -> str:
        """_summary_
            Helper method to read non-empty input from the user. It will keep prompting the user until a non-empty value is provided.
        Args:
            prompt (str): _description_
            input_function (InputFunction): _description_

        Returns:
            str: _description_
        """
        while True:
            value = input_function(prompt).strip()

            if value.lower() == "b":
                return IoHelper.BACK

            if value.lower() == "m":
                return IoHelper.MAIN

            if value:
                return value
            PrintMenu.write("Please enter a value.")

    @staticmethod
    def read_choice(prompt: str, choices: tuple[str, ...], input_function: InputFunction) -> str:
        """_summary_
            Helper method to read a choice from the user. It will keep prompting the user until a valid choice is provided.
        Args:
            prompt (str): prompt to display to the user for input
            choices (tuple[str, ...]): A tuple of valid choices
            input_function (InputFunction): The function to use for user input

        Returns:
            str: The user's choice, which will be one of the valid choices or a navigation command (BACK or MAIN).
        """
        while True:
            value = input_function(prompt).strip().lower()

            if value == "b":
                return IoHelper.BACK

            if value == "m":
                return IoHelper.MAIN

            if value.isdigit() and 1 <= int(value) <= len(choices):
                return choices[int(value) - 1]

            if value in choices:
                return value
            PrintMenu.write(f"Please choose one of: {', '.join(choices)}.")

    @staticmethod
    def read_date(input_function: InputFunction) -> str:
        """_summary_
            Helper method to read a date input from the user in DD-MM-YYYY format. It will keep prompting the user until a valid date is provided.
        Args:
            input_function (InputFunction): The function to use for user input

        Returns:
            str: The user's input date in DD-MM-YYYY format, or a navigation command (BACK or MAIN).
        """
        while True:
            value = IoHelper.read_non_empty(
                "\nDate of loss/finding (DD-MM-YYYY): ",
                input_function,
            )

            if value == IoHelper.BACK:
                return IoHelper.BACK

            if value == IoHelper.MAIN:
                return IoHelper.MAIN

            try:
                occurrence_date = datetime.strptime(value, "%d-%m-%Y").date()
            except ValueError:
                PrintMenu.write("Please use a valid date in DD-MM-YYYY format.")
                continue
            if occurrence_date > date.today():
                PrintMenu.write("The date cannot be in the future.")
                continue

            return value

    @staticmethod
    def read_image_path(input_function: InputFunction) -> str | None:
        """_summary_
            Helper method to read an image file path from the user. It will open a file dialog for the user to select an image file, or allow the user to input the path manually if in a headless environment.
        Args:
            input_function (InputFunction): The function to use for user input

        Returns:
            str | None: The path to the selected image file, or None if the user cancels the selection.
        """
        load_dotenv(Path(__file__).parent.parent / ".env")
        if os.environ.get("APP_CONTAINER") != "1":
            while True:
                try:
                    root = tk.Tk()
                    root.withdraw()

                    file_path = filedialog.askopenfilename(
                        title="Select an image",
                        filetypes=[
                            ("Image files", "*jpg *jpeg *png"),
                            ("JPG files", "*jpg"),
                            ("JPEG files", "*jpeg"),
                            ("PNG files", "*png"),
                        ],
                    )

                    root.destroy()

                    if not file_path:
                        PrintMenu.write("Image selection is cancelled.")
                        return None

                    image_path = Path(file_path)

                    if image_path.suffix.lower() not in IoHelper.IMAGE_EXTENSIONS:
                        PrintMenu.write(
                            "Please submit an image with a .jpg, .jpeg, or .png extension."
                        )
                        continue

                    if not image_path.is_file():
                        PrintMenu.write(
                            "The image file could not be found. Please try again."
                        )
                        continue

                    PrintMenu.write("The image is added successfully. \n")
                    return str(image_path)
                except tk.TclError as error:
                    PrintMenu.write(
                        f"[!] An error occurred while selecting the image: {error}"
                    )

        PrintMenu.write("\n[!] Headless container environment detected. Using CLI input.")
        while True:
            PrintMenu.write("Please enter the full path to the image file.")
            IoHelper.print_nav()
            cli_input = input_function(
                "Enter the image name make sure the image is stored in the /temp "
                "directory (Example: image.jpg): "
            )

            if cli_input.lower() == "b":
                return IoHelper.BACK
            elif cli_input.lower() == "m":
                return IoHelper.MAIN

            image_path = Path("temp/" + cli_input).expanduser()

            if image_path.suffix.lower() not in IoHelper.IMAGE_EXTENSIONS:
                PrintMenu.write(
                    "Please submit an image with a .jpg, .jpeg, or .png extension.\n"
                )
                continue

            if not image_path.is_file():
                PrintMenu.write(
                    "The image file could not be found. Please try again.\n"
                )
                continue

            PrintMenu.write("The image is added successfully.\n")
            return str(image_path)

    @staticmethod
    def print_choices(title: str, choices: tuple[str, ...]) -> None:
        """_summary_
            Displays a list of choices to the user in a formatted manner.
        Args:
            title (str): The title to display above the list of choices.
            choices (tuple[str, ...]): A tuple of choices to display to the user.
        """
        PrintMenu.choices(title, choices)

    @staticmethod
    def print_nav(include_back: bool = True) -> None:
        """_summary_
            Displays navigation options to the user, including the option to go back to the previous step or return to the main menu.
        Args:
            include_back (bool, optional): Whether to include the "back" option. Defaults to True.
        """
        PrintMenu.navigation(include_back)
