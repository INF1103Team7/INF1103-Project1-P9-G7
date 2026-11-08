"""CLI and report-display manager for the lost-and-found application."""

from typing import Callable, Iterable, Mapping

import data_manager
from io_classes import (
    Bag,
    Bottle,
    CATEGORIES,
    Clothing,
    Electronics,
    Format,
    IoHelper,
    Items,
    Keys,
    OtherItem,
    PrintMenu,
    StudentCard,
)

REPORT_TYPES = ("lost", "found")
IMAGE_EXTENSIONS = IoHelper.IMAGE_EXTENSIONS
BACK = IoHelper.BACK
MAIN = IoHelper.MAIN

InputFunction = Callable[[str], str]


class IOManager:
    """Coordinate the command-line input and output helpers."""

    format_record = staticmethod(Format.record)
    format_records = staticmethod(Format.records)

    def collect_report(
        self,
        input_function: InputFunction = input,
    ) -> dict[str, str] | None:
        stage = 1

        report_type = None
        category: Items | None = None
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
                IoHelper.print_choices("\nItem category:", CATEGORIES)
                IoHelper.print_nav()

                selected_category = IoHelper.read_choice(
                    "Select item category: ", CATEGORIES, input_function
                )

                if selected_category == MAIN:
                    return None

                if selected_category == BACK:
                    stage = 1
                    continue

                category = Items.from_value(selected_category)
                stage = 3

            elif stage == 3:
                PrintMenu.write(
                    f"\nEnter item description ({category.description_guidance})."
                )
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
                    "category": category.value,
                    "description": description,
                    "image_path": image_path,
                    "date": occurrence_date,
                }

    @staticmethod
    def display_summary(records: Iterable[Mapping[str, object]]) -> None:
        PrintMenu.display_summary(records)

    def resolve_best_match(
        self,
        best_match: Mapping[str, object],
        input_function: InputFunction = input,
    ) -> bool:
        return PrintMenu.confirm_best_match(best_match, input_function)

    def run_cli(
        self,
        input_function: InputFunction = input,
    ) -> dict[str, str] | str:
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
                report = self.collect_report(input_function)

                if report is None:
                    PrintMenu.write("\nReport submission cancelled.")
                    continue

                PrintMenu.section("Report submitted successfully!", 32)
                return report

            if command in {"2", "/summary", "summary"}:
                try:
                    report_list = data_manager.load_reports()
                except (OSError, ValueError) as error:
                    report_list = []
                    PrintMenu.write(f"Could not load saved reports: {error}")
                self.display_summary(report_list)
            elif command in {"3", "exit", "quit", "q"}:
                PrintMenu.write(
                    "\nExiting the AI powered lost and found system. Goodbye!"
                )
                return "quit"
            else:
                PrintMenu.write("Please choose 1, 2, or 3.")


_default_io_manager = IOManager()
collect_report = _default_io_manager.collect_report
display_summary = _default_io_manager.display_summary
resolve_best_match = _default_io_manager.resolve_best_match
run_cli = _default_io_manager.run_cli
format_record = IOManager.format_record
format_records = IOManager.format_records

__all__ = [
    "Bag",
    "Bottle",
    "CATEGORIES",
    "Clothing",
    "Electronics",
    "Format",
    "IOManager",
    "IMAGE_EXTENSIONS",
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
    IOManager().run_cli()
