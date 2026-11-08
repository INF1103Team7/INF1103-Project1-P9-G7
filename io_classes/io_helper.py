from datetime import date, datetime
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from typing import Callable

from dotenv import load_dotenv

from .print_menu import PrintMenu


InputFunction = Callable[[str], str]


class IoHelper:
    BACK = "BACK"
    MAIN = "MAIN"
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

    @staticmethod
    def read_non_empty(prompt: str, input_function: InputFunction) -> str:
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
    def read_choice(
        prompt: str,
        choices: tuple[str, ...],
        input_function: InputFunction,
    ) -> str:
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
        load_dotenv()
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
        PrintMenu.choices(title, choices)

    @staticmethod
    def print_nav(include_back: bool = True) -> None:
        PrintMenu.navigation(include_back)
