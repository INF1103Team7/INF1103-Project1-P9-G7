

from abc import ABC, abstractmethod
from datetime import date, datetime
import os
from pathlib import Path
import re
from typing import Callable, ClassVar, Iterable, Mapping
import tkinter as tk
from tkinter import filedialog

import data_manager
from dotenv import load_dotenv


REPORT_TYPES = ("lost", "found")
_COLOR_TERMS = (
    "black",
    "blue",
    "brown",
    "clear",
    "gold",
    "gray",
    "green",
    "grey",
    "orange",
    "pink",
    "purple",
    "red",
    "silver",
    "white",
    "yellow",
    "navy",
)
_MATERIAL_TERMS = (
    "canvas",
    "ceramic",
    "fabric",
    "glass",
    "leather",
    "metal",
    "plastic",
    "rubber",
    "steel",
    "stainless",
    "wood",
    "wooden",
)


class Item(ABC):
    """Base class for the supported item categories."""

    description_guidance: ClassVar[str]
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]]

    @property
    @abstractmethod
    def value(self) -> str:
        """Return the category value used by the existing report data format."""

    @classmethod
    def from_value(cls, value: str) -> "Item":
        for item_class in _ITEM_CLASSES:
            item = item_class()
            if item.value == value:
                return item
        raise ValueError(f"Unsupported item category: {value}")

    def validate_description(self, description: str) -> bool:
        """Require one identifying detail from each category-specific group."""
        tokens = re.findall(r"[a-z0-9]+", description.casefold())
        words = set(tokens)
        normalized_description = " ".join(tokens)

        def matches_term(term: str) -> bool:
            if " " in term:
                return term in normalized_description
            return term in words or (
                len(term) >= 4
                and any(word.startswith(term) for word in words)
            )

        return all(
            any(matches_term(term) for term in detail_group)
            for detail_group in self.identifying_detail_groups
        )


class StudentCard(Item):
    value: ClassVar[str] = "student card"
    description_guidance: ClassVar[str] = (
        "the card's appearance or issuer (not its number), plus a distinctive "
        "visible feature"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "color",
            "colour",
            *_COLOR_TERMS,
            "school",
            "sit",
            "design",
            "holder",
            "lanyard",
        ),
        ("sticker", "scratch", "damage", "pattern", "mark", "chip", "crease", "logo"),
    )


class Bottle(Item):
    value: ClassVar[str] = "bottle"
    description_guidance: ClassVar[str] = (
        "its color, material, brand, or lid, plus a distinctive mark or feature"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "color",
            "colour",
            *_COLOR_TERMS,
            "material",
            *_MATERIAL_TERMS,
            "brand",
            "lid",
            "cap",
            "size",
            "metal",
        ),
        ("dent", "scratch", "sticker", "logo", "mark", "handle", "pattern"),
    )


class Keys(Item):
    value: ClassVar[str] = "keys"
    description_guidance: ClassVar[str] = (
        "the keys or keychain, plus a distinctive tag, fob, color, or mark"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "key",
            "keys",
            "keychain",
            "key chain",
            "ring",
            "metal",
            "number",
            *_COLOR_TERMS,
        ),
        (
            "tag",
            "fob",
            "charm",
            "color",
            "colour",
            *_COLOR_TERMS,
            "scratch",
            "mark",
            "shape",
        ),
    )


class Bag(Item):
    value: ClassVar[str] = "bag"
    description_guidance: ClassVar[str] = (
        "its color, size, material, or brand, plus a distinctive pocket, strap, "
        "mark, or feature"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "color",
            "colour",
            *_COLOR_TERMS,
            "size",
            "material",
            "brand",
            "backpack",
            "tote",
        ),
        ("pocket", "strap", "logo", "sticker", "scratch", "mark", "zipper"),
    )


class Clothing(Item):
    value: ClassVar[str] = "clothing"
    description_guidance: ClassVar[str] = (
        "the garment, color, pattern, or material, plus a distinctive logo, "
        "mark, or feature"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "shirt",
            "jacket",
            "pants",
            "trousers",
            "hoodie",
            "coat",
            "color",
            "colour",
            *_COLOR_TERMS,
            "pattern",
            "material",
        ),
        ("logo", "stain", "tear", "mark", "zipper", "button", "pocket", "design"),
    )


class Electronics(Item):
    value: ClassVar[str] = "electronics"
    description_guidance: ClassVar[str] = (
        "the device type, brand, model, or color, plus a distinctive case, "
        "mark, or feature (do not include serial numbers)"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "phone",
            "laptop",
            "tablet",
            "earbuds",
            "headphones",
            "watch",
            "brand",
            "model",
            "color",
            "colour",
            *_COLOR_TERMS,
        ),
        ("case", "sticker", "scratch", "mark", "screen", "button", "crack", "shape"),
    )


class OtherItem(Item):
    value: ClassVar[str] = "others"
    description_guidance: ClassVar[str] = (
        "its type, color, material, or shape, plus a distinctive mark or feature"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "type",
            "color",
            "colour",
            *_COLOR_TERMS,
            "material",
            *_MATERIAL_TERMS,
            "shape",
            "brand",
            "size",
        ),
        ("sticker", "scratch", "mark", "pattern", "damage", "label", "feature"),
    )


_ITEM_CLASSES = (
    StudentCard,
    Bottle,
    Keys,
    Bag,
    Clothing,
    Electronics,
    OtherItem,
)
CATEGORIES = tuple(item_class.value for item_class in _ITEM_CLASSES)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
BACK = "BACK"
MAIN = "MAIN"

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]
ImageSelector = Callable[[], str | None]
ReportLoader = Callable[[], Iterable[Mapping[str, object]]]


class TerminalIO(ABC):
    """Contract for reading from and writing to a user-facing terminal."""

    @abstractmethod
    def read(self, prompt: str) -> str:
        """Read one response from the user."""

    @abstractmethod
    def write(self, message: str) -> None:
        """Display a message to the user."""

    @abstractmethod
    def select_image(self) -> str | None:
        """Select an image, or return a navigation token or None."""


class ConsoleTerminal(TerminalIO):
    """Production terminal adapter using standard input and output."""

    def read(self, prompt: str) -> str:
        return input(prompt)

    def write(self, message: str) -> None:
        print(message)

    def select_image(self) -> str | None:
        return _select_image(input, print)


class CallbackTerminal(TerminalIO):
    """Terminal adapter for tests and other callers supplying callbacks."""

    def __init__(
        self,
        input_function: InputFunction = input,
        output_function: OutputFunction = print,
        image_selector: ImageSelector | None = None,
    ) -> None:
        self._input_function = input_function
        self._output_function = output_function
        self._image_selector = image_selector

    def read(self, prompt: str) -> str:
        return self._input_function(prompt)

    def write(self, message: str) -> None:
        self._output_function(message)

    def select_image(self) -> str | None:
        if self._image_selector is not None:
            return self._image_selector()
        return _select_image(self.read, self.write)


def _read_non_empty(prompt: str, terminal: TerminalIO) -> str:
    while True:
        value = terminal.read(prompt).strip()
        if value.lower() == "b":
            return BACK
        if value.lower() == "m":
            return MAIN
        if value:
            return value
        terminal.write("Please enter a value.")


def _read_item_description(item: Item, terminal: TerminalIO) -> str:
    prompt = f"\nItem description ({item.description_guidance}): "
    while True:
        description = _read_non_empty(prompt, terminal)
        if description in {BACK, MAIN}:
            return description
        if item.validate_description(description):
            return description
        terminal.write(
            "Please add identifying details covering "
            f"{item.description_guidance}."
        )


def _read_choice(
    prompt: str,
    choices: tuple[str, ...],
    terminal: TerminalIO,
) -> str:
    while True:
        value = terminal.read(prompt).strip().lower()
        if value == "b":
            return BACK
        if value == "m":
            return MAIN
        if value.isdigit() and 1 <= int(value) <= len(choices):
            return choices[int(value) - 1]
        if value in choices:
            return value
        terminal.write(f"Please choose one of: {', '.join(choices)}.")


def _read_date(terminal: TerminalIO) -> str:
    while True:
        value = _read_non_empty("\nDate of loss/finding (DD-MM-YYYY): ", terminal)
        if value in {BACK, MAIN}:
            return value
        try:
            occurrence_date = datetime.strptime(value, "%d-%m-%Y").date()
        except ValueError:
            terminal.write("Please use a valid date in DD-MM-YYYY format.")
            continue
        if occurrence_date > date.today():
            terminal.write("The date cannot be in the future.")
            continue
        return value


def _select_image(
    input_function: InputFunction,
    output_function: OutputFunction,
) -> str | None:
    load_dotenv()
    if os.environ.get("APP_CONTAINER") != "1":
        while True:
            root = None
            try:
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename(
                    title="Select an image",
                    filetypes=[
                        ("Image files", "*.jpg *.jpeg *.png"),
                        ("JPG files", "*.jpg"),
                        ("JPEG files", "*.jpeg"),
                        ("PNG files", "*.png"),
                    ],
                )
            except tk.TclError as error:
                output_function(
                    f"[!] Unable to open the image selector: {error}"
                )
                break
            finally:
                if root is not None:
                    try:
                        root.destroy()
                    except tk.TclError as error:
                        output_function(
                            f"[!] Unable to close the image selector: {error}"
                        )

            if not file_path:
                output_function("Image selection is cancelled.")
                return None

            image_path = Path(file_path)
            if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                output_function(
                    "Please submit an image with a .jpg, .jpeg, or .png extension."
                )
                continue
            if not image_path.is_file():
                output_function(
                    "The image file could not be found. Please try again."
                )
                continue

            output_function("The image is added successfully.\n")
            return str(image_path)

    output_function("\n[!] Headless container environment detected. Using CLI input.")
    while True:
        output_function("Please enter the full path to the image file.")
        output_function("B. Go back to the previous step.")
        output_function("M. Go back to the Main Menu")
        cli_input = input_function(
            "Enter the image name make sure the image is stored in the /temp "
            "directory (Example: image.jpg): "
        ).strip()
        if cli_input.lower() == "b":
            return BACK
        if cli_input.lower() == "m":
            return MAIN

        image_path = Path("temp/" + cli_input).expanduser()
        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            output_function(
                "Please submit an image with a .jpg, .jpeg, or .png extension.\n"
            )
            continue
        if not image_path.is_file():
            output_function("The image file could not be found. Please try again.\n")
            continue

        output_function("The image is added successfully.\n")
        return str(image_path)


def _print_choices(
    title: str,
    choices: tuple[str, ...],
    terminal: TerminalIO,
) -> None:
    terminal.write(title)
    for number, choice in enumerate(choices, start=1):
        terminal.write(f"{number}. {choice.title()}")


def _print_nav(terminal: TerminalIO, include_back: bool = True) -> None:
    if include_back:
        terminal.write("B. Go back to the previous step.")
    terminal.write("M. Go back to the Main Menu")


class ReportCollector:
    """Collect and validate a report using a terminal for one collection."""

    def collect(
        self, terminal: TerminalIO
    ) -> dict[str, str | None] | None:
        stage = 1
        report_type = None
        category = None
        description = None
        image_path = None
        occurrence_date = None

        while True:
            if stage == 1:
                _print_choices("\nReport type:", REPORT_TYPES, terminal)
                _print_nav(terminal, include_back=False)
                selected_report_type = _read_choice(
                    "Select report type: ", REPORT_TYPES, terminal
                )
                if selected_report_type == MAIN:
                    return None
                report_type = selected_report_type
                stage = 2
            elif stage == 2:
                _print_choices("\nItem category:", CATEGORIES, terminal)
                _print_nav(terminal)
                selected_category = _read_choice(
                    "Select item category: ", CATEGORIES, terminal
                )
                if selected_category == MAIN:
                    return None
                if selected_category == BACK:
                    stage = 1
                    continue
                category = Item.from_value(selected_category)
                stage = 3
            elif stage == 3:
                terminal.write("\nEnter item description.")
                _print_nav(terminal)
                description = _read_item_description(category, terminal)
                if description == MAIN:
                    return None
                if description == BACK:
                    stage = 2
                    continue
                stage = 4
            elif stage == 4:
                _print_choices(
                    "\nWould you like to upload an image?",
                    ("yes", "no"),
                    terminal,
                )
                _print_nav(terminal)
                upload_image = _read_choice(
                    "Select an option: ", ("yes", "no"), terminal
                )
                if upload_image == MAIN:
                    return None
                if upload_image == BACK:
                    stage = 3
                    continue
                image_path = None
                if upload_image == "yes":
                    image_path = terminal.select_image()
                    if image_path == BACK:
                        continue
                    if image_path == MAIN:
                        return None
                stage = 5
            else:
                terminal.write("\nEnter the date of loss/finding.")
                _print_nav(terminal)
                occurrence_date = _read_date(terminal)
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


def format_record(record: Mapping[str, object]) -> str:
    """Format one report without performing terminal I/O."""
    report_type = str(
        record.get("report_type", record.get("type", "unknown"))
    ).title()
    case_id = str(record.get("case_id", "unknown"))
    status = str(record.get("status", "Unknown"))
    category = str(record.get("category", "unknown")).title()
    identifying_features = record.get(
        "identifying_features", "No identifying features"
    )
    image_path = str(
        record.get(
            "image_filename",
            record.get("image_path", record.get("image", "No image")),
        )
    )
    occurrence_date = str(
        record.get("date", record.get("occurrence_date", "Unknown date"))
    )
    features = (
        ", ".join(identifying_features)
        if isinstance(identifying_features, list)
        else identifying_features
    )
    return (
        f"{report_type} report\n"
        f"  Case ID: {case_id}\n"
        f"  Status: {status}\n"
        f"  Category: {category}\n"
        f"  Identifying Features: {features}\n"
        f"  Date: {occurrence_date}\n"
        f"  Image: {image_path}"
    )


def format_records(records: Iterable[Mapping[str, object]]) -> str:
    """Format multiple reports without performing terminal I/O."""
    record_list = list(records)
    if not record_list:
        return "No reports found."
    return "\n\n".join(
        f"{number}. {format_record(record)}"
        for number, record in enumerate(record_list, start=1)
    )


class IOManager:
    """Coordinate terminal interactions and report presentation."""

    def __init__(
        self,
        terminal: TerminalIO | None = None,
        report_loader: ReportLoader = data_manager.load_reports,
    ) -> None:
        self._terminal = terminal if terminal is not None else ConsoleTerminal()
        self._report_loader = report_loader
        self._collector = ReportCollector()

    def collect_report(self) -> dict[str, str | None] | None:
        return self._collector.collect(self._terminal)

    def display_summary(self, records: Iterable[Mapping[str, object]]) -> None:
        self._terminal.write("\nLost-and-Found Summary")
        self._terminal.write("======================")
        self._terminal.write(format_records(records))

    def resolve_best_match(
        self, best_match: Mapping[str, object]
    ) -> bool:
        self._terminal.write("[+] Best match found from database:")
        evaluation = best_match.get("evaluation")
        if not isinstance(evaluation, Mapping):
            raise ValueError("The best match must include an evaluation mapping.")

        matched_rules = evaluation.get("matched_rules_list")
        mismatched_rules = evaluation.get("mismatched_rules_list")
        self._terminal.write(f"Verdict: {evaluation.get('status')}")
        self._terminal.write(
            "Final score after applying business rules: "
            f"{evaluation.get('final_composite_score')}/100"
        )
        self._terminal.write(
            "Matched rules: "
            f"{', '.join(matched_rules) if matched_rules else 'None'}"
        )
        self._terminal.write(
            "Mismatched rules: "
            f"{', '.join(mismatched_rules) if mismatched_rules else 'None'}"
        )
        self._terminal.write(f"Summary: {evaluation.get('evaluation_summary')}")

        while True:
            resolve = self._terminal.read(
                "Is this a match for the item you have lost? (yes/no): "
            ).strip().lower()
            if resolve in {"yes", "y"}:
                return True
            if resolve in {"no", "n"}:
                return False
            self._terminal.write("Please enter 'yes' or 'no'.")

    def run_cli(self) -> dict[str, str | None] | str:
        while True:
            self._terminal.write("\n" + "=" * 50)
            self._terminal.write("Welcome to the AI powered lost and found system!")
            self._terminal.write("=" * 50)
            self._terminal.write("1. Submit a lost/found report")
            self._terminal.write("2. View summary of all reports")
            self._terminal.write("3. Exit")
            command = self._terminal.read("Select an option: ").strip().lower()

            if command in {"1", "report", "submit"}:
                report = self.collect_report()
                if report is None:
                    self._terminal.write("\nReport submission cancelled.")
                    continue
                self._terminal.write("\n" + "=" * 32)
                self._terminal.write("Report submitted successfully!")
                self._terminal.write("=" * 32)
                return report
            if command in {"2", "/summary", "summary"}:
                try:
                    report_list = self._report_loader()
                except (OSError, ValueError) as error:
                    self._terminal.write(f"Could not load saved reports: {error}")
                    report_list = []
                self.display_summary(report_list)
                continue
            if command in {"3", "exit", "quit", "q"}:
                self._terminal.write(
                    "\nExiting the AI powered lost and found system. Goodbye!"
                )
                return "quit"
            self._terminal.write("Please choose 1, 2, or 3.")


def collect_report(
    input_function: InputFunction = input,
    output_function: OutputFunction = print,
) -> dict[str, str | None] | None:
    terminal = CallbackTerminal(input_function, output_function)
    return IOManager(terminal).collect_report()


def display_summary(
    records: Iterable[Mapping[str, object]],
    output_function: OutputFunction = print,
) -> None:
    terminal = CallbackTerminal(output_function=output_function)
    IOManager(terminal).display_summary(records)


def resolve_best_match(
    best_match: Mapping[str, object],
    input_function: InputFunction = input,
    output_function: OutputFunction = print,
) -> bool:
    terminal = CallbackTerminal(input_function, output_function)
    return IOManager(terminal).resolve_best_match(best_match)


def run_cli(
    input_function: InputFunction = input,
    output_function: OutputFunction = print,
) -> dict[str, str | None] | str:
    terminal = CallbackTerminal(input_function, output_function)
    return IOManager(terminal).run_cli()


__all__ = [
    "CATEGORIES",
    "Bag",
    "Bottle",
    "Clothing",
    "Electronics",
    "Item",
    "Keys",
    "OtherItem",
    "REPORT_TYPES",
    "StudentCard",
    "CallbackTerminal",
    "ConsoleTerminal",
    "IOManager",
    "ReportCollector",
    "TerminalIO",
    "collect_report",
    "display_summary",
    "format_record",
    "format_records",
    "resolve_best_match",
    "run_cli",
]


if __name__ == "__main__":
    run_cli()
