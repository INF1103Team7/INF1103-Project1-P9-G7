# CLI and report-display manager for the lost-and-found application..

# Imports
import data_manager
from typing import Callable, Iterable, Mapping
from logic_manager import LogicManager
from logic_classes.threshold_config import ThresholdConfig
from io_classes import (
    Format,
    IoHelper,
    Items,
    PrintMenu,
)

# Constants
REPORT_TYPES = ("lost", "found")
IMAGE_EXTENSIONS = IoHelper.IMAGE_EXTENSIONS
BACK = IoHelper.BACK
MAIN = IoHelper.MAIN

InputFunction = Callable[[str], str]

# Class to manage the command-line input and output for the lost-and-found application
class IOManager:

    format_record = staticmethod(Format.record)
    format_records = staticmethod(Format.records)

    def collect_report(self, input_function: InputFunction = input) -> dict[str, str] | None:
        """_summary_
            Function to collect a lost or found report from the user through a command-line interface.
        Args:
            input_function (InputFunction, optional): The function to use for reading user input. Defaults to input.

        Returns:
            dict[str, str] | None: A dictionary containing the report details if the report is successfully collected, or None if the user cancels the report submission.
        """
        stage = 1

        report_type = None
        category = ""
        description = None
        image_path = None
        occurrence_date = None

        while True:
            if stage == 1:
                IoHelper.print_choices("\nReport type:", REPORT_TYPES)
                IoHelper.print_nav(include_back=False)

                report_type = IoHelper.read_choice(
                    "Select report type: ", REPORT_TYPES, input_function
                )

                if report_type == MAIN:
                    return None

                stage = 2

            elif stage == 2:
                IoHelper.print_choices("\nItem category:", Items.categories())
                IoHelper.print_nav()

                category = IoHelper.read_choice(
                    "Select item category: ", Items.categories(), input_function
                )

                if category == MAIN:
                    return None

                if category == BACK:
                    stage = 1
                    continue

                stage = 3

            elif stage == 3:
                PrintMenu.write("\nEnter item description.")
                IoHelper.print_nav()

                description = IoHelper.read_non_empty(
                    "\nItem description: ", input_function
                )

                if description == MAIN:
                    return None

                if description == BACK:
                    stage = 2
                    continue

                stage = 4

            elif stage == 4:
                IoHelper.print_choices(
                    "\nWould you like to upload an image?", ("yes", "no")
                )
                IoHelper.print_nav()

                upload_image = IoHelper.read_choice(
                    "Select an option: ", ("yes", "no"), input_function
                )

                if upload_image == MAIN:
                    return None

                if upload_image == BACK:
                    stage = 3
                    continue

                image_path = None
                if upload_image == "yes":
                    image_path = IoHelper.read_image_path(input_function)

                    if image_path is BACK:
                        continue
                    if image_path == MAIN:
                        break
                stage = 5

            elif stage == 5:
                PrintMenu.write("\nEnter the date of loss/finding.")
                IoHelper.print_nav()

                occurrence_date = IoHelper.read_date(input_function)

                if occurrence_date == MAIN:
                    return None

                if occurrence_date == BACK:
                    stage = 4
                    continue

                return {
                    "report_type": report_type,
                    "category": category,
                    "description": description,
                    "image_path": image_path,
                    "date": occurrence_date,
                }

    @staticmethod
    def display_summary(records: Iterable[Mapping[str, object]]) -> None:
        """_summary_
            Displays a summary of lost and found reports in a formatted manner.
        Args:
            records (Iterable[Mapping[str, object]]): An iterable of dictionaries, each representing a report with its details.
        """
        PrintMenu.display_summary(records)

    def resolve_best_match(self, best_match: Mapping[str, object], input_function: InputFunction = input) -> bool:
        """_summary_
            Resolves the best match for a lost report by prompting the user for confirmation.
        Args:
            best_match (Mapping[str, object]): A dictionary containing the details of the best match report.
            input_function (InputFunction, optional): The function to use for reading user input. Defaults to input.

        Returns:
            bool: True if the user confirms the match, False otherwise.
        """
        return PrintMenu.confirm_best_match(best_match, input_function)

    def run_cli(self,input_function: InputFunction = input, current_logic=None) -> dict[str, str] | str:
        """_summary_
            Runs the command-line interface for the lost-and-found application, allowing users to submit reports, view summaries, and configure system settings.
        Args:
            input_function (InputFunction, optional): The function to use for reading user input. Defaults to input.
            current_logic (_type_, optional): The current logic class to use. Defaults to None.

        Returns:
            dict[str, str] | str: A dictionary containing the report details if a report is submitted, or "quit" if the user chooses to exit the application.
        """
        data = data_manager.DataManager()
        while True:
            PrintMenu.section(
                "Welcome to the AI powered lost and found system!",
                50,
            )
            PrintMenu.write("1. Submit a lost/found report")
            PrintMenu.write("2. View summary of all reports")
            PrintMenu.write("3. Configure system settings")
            PrintMenu.write("4. Exit")
            command = input_function("Select an option: ").strip().lower()

            if command in {"1", "report", "submit"}:
                report = self.collect_report(input_function)

                if report is None:
                    PrintMenu.write("\nReport submission cancelled.")
                    continue

                PrintMenu.section("Report submitted successfully!", 32)
                return report, current_logic

            elif command in {"2", "/summary", "summary"}:
                try:
                    report_list = data.load_reports()
                except (OSError, ValueError) as error:
                    report_list = []
                    PrintMenu.write(f"Could not load saved reports: {error}")
                self.display_summary(report_list)
            
            elif command in {"3", "config", "settings"}:
                reject, high, min_strong, min_excellent, consider_location = PrintMenu.configure_threshhold()
                PrintMenu.write("[+] Applying new configuration settings")
                threshold_config = ThresholdConfig(reject, high, min_strong, min_excellent)
                threshold_config.consider_location = consider_location
                
                logic = LogicManager(threshold_config=threshold_config)
                PrintMenu.write("[+] New configuration settings applied successfully")
                return None, logic
            
            elif command in {"4", "exit", "quit", "q"}:
                PrintMenu.write(
                    "\nExiting the AI powered lost and found system. Goodbye!"
                )
                return "quit", None
            else:
                PrintMenu.write("Please choose 1, 2, 3 or 4.")


_default_io_manager = IOManager()
collect_report = _default_io_manager.collect_report
display_summary = _default_io_manager.display_summary
resolve_best_match = _default_io_manager.resolve_best_match
run_cli = _default_io_manager.run_cli
format_record = IOManager.format_record
format_records = IOManager.format_records

__all__ = ["IOManager"]

if __name__ == "__main__":
    IOManager().run_cli()
