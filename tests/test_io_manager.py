
from io_classes.formatting import Format
from io_classes.io_helper import IoHelper
from datetime import date, timedelta
from pathlib import Path
from io_classes.print_menu import PrintMenu
import pytest
from io_manager import IOManager
import tkinter as tk
import io_classes.io_helper as io_helper_module
from io_classes.io_helper import IoHelper

def test_format_single_record():
    report = {
        "report_type": "lost",
        "case_id": "CASE001",
        "status": "Pending",
        "category": "bottle",
        "identifying_features": ["black cap", "white logo"],
        "date": "09-11-2026",
        "image_filename": "bottle.jpg",
    }

    result = Format.record(report)

    assert "Lost report" in result
    assert "Case ID: CASE001" in result
    assert "Status: Pending" in result
    assert "Category: Bottle" in result
    assert "Identifying Features: black cap, white logo" in result
    assert "Date: 09-11-2026" in result
    assert "Image: bottle.jpg" in result


def test_format_multiple_records():
    reports = [
        {
            "report_type": "lost",
            "case_id": "CASE001",
            "category": "bottle",
        },
        {
            "report_type": "found",
            "case_id": "CASE002",
            "category": "keys",
        },
    ]

    result = Format.records(reports)

    assert "1. Lost report" in result
    assert "Case ID: CASE001" in result
    assert "2. Found report" in result
    assert "Case ID: CASE002" in result


def test_format_empty_records():
    reports = []

    result = Format.records(reports)

    assert result == "No reports found."


def test_read_non_empty_valid():
    simulated_input = lambda prompt: "Black water bottle"

    result = IoHelper.read_non_empty(
        "Enter description: ",
        simulated_input
    )

    assert result == "Black water bottle"


def test_read_non_empty_retry():
    inputs = iter(["", "Black water bottle"])

    simulated_input = lambda prompt: next(inputs)

    result = IoHelper.read_non_empty(
        "Enter description: ",
        simulated_input
    )

    assert result == "Black water bottle"


def test_read_non_empty_back():
    simulated_input = lambda prompt: "b"

    result = IoHelper.read_non_empty(
        "Enter description: ",
        simulated_input
    )

    assert result == IoHelper.BACK


def test_read_non_empty_main():
    simulated_input = lambda prompt: "m"

    result = IoHelper.read_non_empty(
        "Enter description: ",
        simulated_input
    )

    assert result == IoHelper.MAIN


def test_read_choice_number():
    choices = ("lost", "found")

    simulated_input = lambda prompt: "2"

    result = IoHelper.read_choice(
        "Select report type: ",
        choices,
        simulated_input
    )

    assert result == "found"


def test_read_choice_text():
    choices = ("lost", "found")

    simulated_input = lambda prompt: "LOST"

    result = IoHelper.read_choice(
        "Select report type: ",
        choices,
        simulated_input
    )

    assert result == "lost"


def test_read_choice_invalid_retry():
    choices = ("lost", "found")

    inputs = iter(["5", "1"])
    simulated_input = lambda prompt: next(inputs)

    result = IoHelper.read_choice(
        "Select report type: ",
        choices,
        simulated_input
    )

    assert result == "lost"


def test_read_choice_back():
    choices = ("lost", "found")

    result = IoHelper.read_choice(
        "Select report type: ",
        choices,
        lambda prompt: "B"
    )

    assert result == IoHelper.BACK


def test_read_choice_main():
    choices = ("lost", "found")

    result = IoHelper.read_choice(
        "Select report type: ",
        choices,
        lambda prompt: "M"
    )

    assert result == IoHelper.MAIN


def test_read_date_valid():
    simulated_input = lambda prompt: "01-01-2025"

    result = IoHelper.read_date(simulated_input)

    assert result == "01-01-2025"


def test_read_date_invalid_format():
    inputs = iter(["2025-01-01", "01-01-2025"])

    result = IoHelper.read_date(lambda prompt: next(inputs))

    assert result == "01-01-2025"


def test_read_date_nonexistent():
    inputs = iter(["31-02-2025", "01-01-2025"])

    result = IoHelper.read_date(lambda prompt: next(inputs))

    assert result == "01-01-2025"


def test_read_date_future():
    future_date = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y")

    inputs = iter([future_date, "01-01-2025"])

    result = IoHelper.read_date(lambda prompt: next(inputs))

    assert result == "01-01-2025"


def test_read_date_back():
    result = IoHelper.read_date(lambda prompt: "b")

    assert result == IoHelper.BACK


def test_read_date_main():
    result = IoHelper.read_date(lambda prompt: "m")

    assert result == IoHelper.MAIN

# monkeypatch:  temporarily changes environment variables and other values during a test.
# tmp_path: creates a temporary directory that pytest automatically manages
def test_read_image_path_valid(monkeypatch, tmp_path):
    # forces the method to use CLI mode instead of opening Tkinter
    monkeypatch.setenv("APP_CONTAINER", "1")
    # temporarily changes the working directory to the test's temporary directory
    monkeypatch.chdir(tmp_path)

    temp_folder = tmp_path / "temp"
    temp_folder.mkdir()

    image_file = temp_folder / "bottle.jpg"
    # Since code only checks the extension and whether the file exists, so fake bytes are sufficient
    image_file.write_bytes(b"fake image data")

    result = IoHelper.read_image_path(
        lambda prompt: "bottle.jpg"
    )

    assert result == str(image_file.relative_to(tmp_path))


def test_read_image_path_invalid_extension(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_CONTAINER", "1")
    monkeypatch.chdir(tmp_path)

    temp_folder = tmp_path / "temp"
    temp_folder.mkdir()

    image_file = temp_folder / "bottle.jpg"
    image_file.write_bytes(b"fake image data")

    inputs = iter(["document.txt", "bottle.jpg"])

    result = IoHelper.read_image_path(
        lambda prompt: next(inputs)
    )

    assert result == str(Path("temp") / "bottle.jpg")


def test_read_image_path_missing_file(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_CONTAINER", "1")
    monkeypatch.chdir(tmp_path)

    temp_folder = tmp_path / "temp"
    temp_folder.mkdir()

    image_file = temp_folder / "bottle.jpg"
    image_file.write_bytes(b"fake image data")

    inputs = iter(["missing.jpg", "bottle.jpg"])

    result = IoHelper.read_image_path(
        lambda prompt: next(inputs)
    )

    assert result == str(Path("temp") / "bottle.jpg")


def test_read_image_path_back(monkeypatch):
    monkeypatch.setenv("APP_CONTAINER", "1")

    result = IoHelper.read_image_path(
        lambda prompt: "b"
    )

    assert result == IoHelper.BACK


def test_read_image_path_main(monkeypatch):
    monkeypatch.setenv("APP_CONTAINER", "1")

    result = IoHelper.read_image_path(
        lambda prompt: "m"
    )

    assert result == IoHelper.MAIN

# capsys: captures anything printed to the terminal, allowing us to check whether the correct messages were displayed #
def test_print_menu_write(capsys):
    PrintMenu.write("Hello World")
    # returns the captured output
    captured = capsys.readouterr()
    # .out to access what was printed and .strip() to remove the trailing newline
    assert captured.out.strip() == "Hello World"

def test_print_menu_choices(capsys):
    PrintMenu.choices("Report type:", ("lost", "found"))

    captured = capsys.readouterr()

    assert "Report type:" in captured.out
    assert "1. Lost" in captured.out
    assert "2. Found" in captured.out


def test_print_menu_navigation_with_back(capsys):
    PrintMenu.navigation(include_back=True)

    captured = capsys.readouterr()

    assert "B. Go back to the previous step." in captured.out
    assert "M. Go back to the Main Menu" in captured.out


def test_print_menu_navigation_without_back(capsys):
    PrintMenu.navigation(include_back=False)

    captured = capsys.readouterr()

    assert "B. Go back to the previous step." not in captured.out
    assert "M. Go back to the Main Menu" in captured.out


def test_print_menu_section(capsys):
    PrintMenu.section(
        "Welcome",
        10,
        leading_newline=False
    )

    captured = capsys.readouterr()

    assert captured.out == "==========\nWelcome\n==========\n"


def test_display_summary_with_reports(capsys):
    reports = [
        {
            "report_type": "lost",
            "case_id": "CASE001",
            "category": "bottle",
        },
        {
            "report_type": "found",
            "case_id": "CASE002",
            "category": "keys",
        },
    ]

    PrintMenu.display_summary(reports)

    captured = capsys.readouterr()

    assert "Lost-and-Found Summary" in captured.out
    assert "1. Lost report" in captured.out
    assert "Case ID: CASE001" in captured.out
    assert "2. Found report" in captured.out
    assert "Case ID: CASE002" in captured.out


def test_display_summary_empty(capsys):
    PrintMenu.display_summary([])

    captured = capsys.readouterr()

    assert "Lost-and-Found Summary" in captured.out
    assert "No reports found." in captured.out


def test_print_best_match(capsys):
    evaluation = {
        "status": "RECOMMENDED_MATCH",
        "final_composite_score": 85,
        "matched_rules_list": ["color", "brand"],
        "mismatched_rules_list": ["location"],
        "evaluation_summary": "Strong similarity detected.",
    }

    PrintMenu.best_match(evaluation)

    captured = capsys.readouterr()

    assert "Best match found from database:" in captured.out
    assert "Verdict: RECOMMENDED_MATCH" in captured.out
    assert "85/100" in captured.out
    assert "Matched rules: color, brand" in captured.out
    assert "Mismatched rules: location" in captured.out
    assert "Summary: Strong similarity detected." in captured.out


def test_print_best_match_no_rules(capsys):
    evaluation = {
        "status": "NO_MATCH",
        "final_composite_score": 20,
        "matched_rules_list": [],
        "mismatched_rules_list": [],
        "evaluation_summary": "Insufficient matching information.",
    }

    PrintMenu.best_match(evaluation)

    captured = capsys.readouterr()

    assert "Verdict: NO_MATCH" in captured.out
    assert "Matched rules: None" in captured.out
    assert "Mismatched rules: None" in captured.out


def test_display_location_alternatives_valid(capsys):
    best_report = {"case_id": "CASE001"}

    alternative_report = {
        "case_id": "CASE002",
        "report_type": "found",
        "category": "bottle",
        "location_lost": "Library",
        "similarity_analysis": {
            "color_match": "match",
            "material_match": "match",
            "brand_match": "match",
            "feature_overlap_match": ["logo"],
            "location_match": "not match",
        },
    }

    best_match = {"report": best_report}

    PrintMenu.display_location_alternatives(
        [best_report, alternative_report],
        best_match
    )

    captured = capsys.readouterr()

    assert "Other reports matching all traits except location:" in captured.out
    assert "Case ID: CASE002" in captured.out
    assert "Location: Library" in captured.out
    assert "Case ID: CASE001" not in captured.out


def test_display_location_alternatives_none(capsys):
    best_match = {
        "report": {"case_id": "CASE001"}
    }

    reports = [
        {
            "case_id": "CASE002",
            "similarity_analysis": {
                "color_match": "not match",
                "material_match": "match",
                "brand_match": "match",
                "feature_overlap_match": ["logo"],
                "location_match": "not match",
            },
        }
    ]

    PrintMenu.display_location_alternatives(
        reports,
        best_match
    )

    captured = capsys.readouterr()

    assert "No other reports match every trait except location." in captured.out


def test_confirm_best_match_yes():
    best_match = {
        "evaluation": {
            "status": "RECOMMENDED_MATCH",
            "final_composite_score": 85,
            "matched_rules_list": ["color", "brand"],
            "mismatched_rules_list": [],
            "evaluation_summary": "Strong match",
        }
    }

    result = PrintMenu.confirm_best_match(
        best_match,
        input_function=lambda prompt: "yes"
    )

    assert result is True


def test_confirm_best_match_no(capsys):
    best_match = {
        "report": {"case_id": "CASE001"},
        "evaluation": {
            "status": "RECOMMENDED_MATCH",
            "final_composite_score": 85,
            "matched_rules_list": ["color"],
            "mismatched_rules_list": [],
            "evaluation_summary": "Strong match",
        },
    }

    result = PrintMenu.confirm_best_match(
        best_match,
        input_function=lambda prompt: "no",
        alternative_matches=[]
    )

    captured = capsys.readouterr()

    assert result is False
    assert "No other reports match every trait except location." in captured.out


def test_confirm_best_match_invalid_retry(capsys):
    best_match = {
        "evaluation": {
            "status": "RECOMMENDED_MATCH",
            "final_composite_score": 85,
            "matched_rules_list": [],
            "mismatched_rules_list": [],
            "evaluation_summary": "Strong match",
        }
    }

    inputs = iter(["maybe", "yes"])

    result = PrintMenu.confirm_best_match(
        best_match,
        input_function=lambda prompt: next(inputs)
    )

    captured = capsys.readouterr()

    assert result is True
    assert "Please enter 'yes' or 'no'." in captured.out


def test_confirm_best_match_missing_evaluation():
    best_match = {
        "report": {"case_id": "CASE001"}
    }

    with pytest.raises(ValueError):
        PrintMenu.confirm_best_match(
            best_match,
            input_function=lambda prompt: "yes"
        )


def test_collect_report_success():
    manager = IOManager()

    inputs = iter([
        "1",                  # Lost report
        "2",                  # Bottle
        "Black water bottle", # Description
        "2",                  # No image upload
        "01-01-2025",         # Date
    ])

    result = manager.collect_report(
        input_function=lambda prompt: next(inputs)
    )

    assert result == {
        "report_type": "lost",
        "category": "bottle",
        "description": "Black water bottle",
        "image_path": None,
        "date": "01-01-2025",
    }


def test_collect_report_cancel():
    manager = IOManager()

    result = manager.collect_report(
        input_function=lambda prompt: "m"
    )

    assert result is None


def test_collect_report_back_navigation():
    manager = IOManager()

    inputs = iter([
        "1",                  # Initially select Lost
        "b",                  # Go back from category
        "2",                  # Change report type to Found
        "2",                  # Select Bottle
        "Black water bottle", # Description
        "2",                  # No image
        "01-01-2025",         # Date
    ])

    result = manager.collect_report(
        input_function=lambda prompt: next(inputs)
    )

    assert result["report_type"] == "found"
    assert result["category"] == "bottle"


def test_collect_report_back_from_description():
    manager = IOManager()

    inputs = iter([
        "1",                  # Lost report
        "2",                  # Initially select Bottle
        "b",                  # Back from description to category
        "3",                  # Change category to Keys
        "Black keychain",     # Description
        "2",                  # No image
        "01-01-2025",         # Date
    ])

    result = manager.collect_report(
        input_function=lambda prompt: next(inputs)
    )

    assert result["category"] == "keys"
    assert result["description"] == "Black keychain"


def test_collect_report_back_from_image():
    manager = IOManager()

    inputs = iter([
        "1",                  # Lost report
        "2",                  # Bottle
        "Black bottle",       # Original description
        "b",                  # Back from image selection
        "White bottle",       # Updated description
        "2",                  # No image
        "01-01-2025",         # Date
    ])

    result = manager.collect_report(
        input_function=lambda prompt: next(inputs)
    )

    assert result["description"] == "White bottle"


def test_collect_report_back_from_date():
    manager = IOManager()

    inputs = iter([
        "1",                  # Lost report
        "2",                  # Bottle
        "Black bottle",       # Description
        "2",                  # No image
        "b",                  # Back from date stage
        "2",                  # Select no image again
        "01-01-2025",         # Valid date
    ])

    result = manager.collect_report(
        input_function=lambda prompt: next(inputs)
    )

    assert result["image_path"] is None
    assert result["date"] == "01-01-2025"


def test_collect_report_cancel_from_description():
    manager = IOManager()

    inputs = iter([
        "1",  # Lost report
        "2",  # Bottle
        "m",  # Return to main menu
    ])

    result = manager.collect_report(
        input_function=lambda prompt: next(inputs)
    )

    assert result is None


def test_collect_report_cancel_from_date():
    manager = IOManager()

    inputs = iter([
        "1",           # Lost report
        "2",           # Bottle
        "Black bottle",
        "2",           # No image
        "m",           # Cancel at date stage
    ])

    result = manager.collect_report(
        input_function=lambda prompt: next(inputs)
    )

    assert result is None


def test_run_cli_exit(capsys):
    manager = IOManager()

    result = manager.run_cli(
        input_function=lambda prompt: "3"
    )

    captured = capsys.readouterr()

    assert result == "quit"
    assert "Exiting the AI powered lost and found system." in captured.out


def test_run_cli_submit_report(capsys):
    manager = IOManager()

    inputs = iter([
        "1",                  # Submit report
        "1",                  # Lost
        "2",                  # Bottle
        "Black water bottle", # Description
        "2",                  # No image
        "01-01-2025",         # Date
    ])

    result = manager.run_cli(
        input_function=lambda prompt: next(inputs)
    )

    captured = capsys.readouterr()

    assert result["report_type"] == "lost"
    assert result["category"] == "bottle"
    assert result["description"] == "Black water bottle"
    assert "Report submitted successfully!" in captured.out


def test_run_cli_invalid_option(capsys):
    manager = IOManager()

    inputs = iter(["9", "3"])

    result = manager.run_cli(
        input_function=lambda prompt: next(inputs)
    )

    captured = capsys.readouterr()

    assert "Please choose 1, 2, or 3." in captured.out
    assert result == "quit"

# monkeypatch temporarily replaces load_reports() with a function that returns sample data so dont need actual saved reports; connect to db
def test_run_cli_summary(monkeypatch, capsys):
    manager = IOManager()

    fake_reports = [
        {
            "report_type": "lost",
            "case_id": "CASE001",
            "category": "bottle",
        },
        {
            "report_type": "found",
            "case_id": "CASE002",
            "category": "keys",
        },
    ]

    monkeypatch.setattr(
        "io_manager.data_manager.load_reports",
        lambda: fake_reports
    )

    inputs = iter(["2", "3"])

    result = manager.run_cli(
        input_function=lambda prompt: next(inputs)
    )

    captured = capsys.readouterr()

    assert result == "quit"
    assert "Lost-and-Found Summary" in captured.out
    assert "Case ID: CASE001" in captured.out
    assert "Case ID: CASE002" in captured.out


def test_run_cli_summary_error(monkeypatch, capsys):
    manager = IOManager()

    def fake_load_reports():
        raise OSError("Database unavailable")

    monkeypatch.setattr(
        "io_manager.data_manager.load_reports",
        fake_load_reports
    )

    inputs = iter(["2", "3"])

    result = manager.run_cli(
        input_function=lambda prompt: next(inputs)
    )

    captured = capsys.readouterr()

    assert result == "quit"
    assert "Could not load saved reports: Database unavailable" in captured.out
    assert "No reports found." in captured.out


def test_collect_report_main_at_category():
    manager = IOManager()

    inputs = iter(["1", "m"])

    result = manager.collect_report(
        lambda prompt: next(inputs)
    )

    assert result is None


def test_collect_report_back_at_image_path(monkeypatch):
    manager = IOManager()

    inputs = iter([
        "1",       # Report type
        "1",       # Category
        "Bottle",  # Description
        "yes",     # Upload image
        "no",      # After returning to image question
        "01-01-2026"
    ])

    from io_classes import IoHelper

    monkeypatch.setattr(
        IoHelper,
        "read_image_path",
        lambda input_function: IoHelper.BACK
    )

    result = manager.collect_report(
        lambda prompt: next(inputs)
    )

    assert result is not None
    assert result["image_path"] is None


def test_collect_report_main_at_image_path(monkeypatch):
    manager = IOManager()

    inputs = iter([
        "1",
        "1",
        "Bottle",
        "yes"
    ])

    from io_classes import IoHelper

    monkeypatch.setattr(
        IoHelper,
        "read_image_path",
        lambda input_function: IoHelper.MAIN
    )

    result = manager.collect_report(
        lambda prompt: next(inputs)
    )

    assert result is None


def test_collect_report_back_at_date(monkeypatch):
    manager = IOManager()

    from io_classes import IoHelper

    inputs = iter([
        "1",
        "1",
        "Bottle",
        "no",
        "no"
    ])

    dates = iter([
        IoHelper.BACK,
        "01-01-2026"
    ])

    monkeypatch.setattr(
        IoHelper,
        "read_date",
        lambda input_function: next(dates)
    )

    result = manager.collect_report(
        lambda prompt: next(inputs)
    )

    assert result is not None
    assert result["image_path"] is None


def test_run_cli_cancel_submission(monkeypatch):
    manager = IOManager()

    monkeypatch.setattr(
        manager,
        "collect_report",
        lambda input_function: None
    )

    inputs = iter([
        "1",  # Submit report
        "3"   # Exit after cancellation
    ])

    result = manager.run_cli(
        lambda prompt: next(inputs)
    )

    assert result == "quit"

def test_image_dialog_cancel(monkeypatch):
    monkeypatch.setattr(
        io_helper_module,
        "load_dotenv",
        lambda: None
    )
    monkeypatch.delenv("APP_CONTAINER", raising=False)

    class FakeRoot:
        def withdraw(self):
            pass

        def destroy(self):
            pass

    monkeypatch.setattr(tk, "Tk", lambda: FakeRoot())

    monkeypatch.setattr(
        io_helper_module.filedialog,
        "askopenfilename",
        lambda **kwargs: ""
    )

    result = IoHelper.read_image_path(lambda prompt: "")

    assert result is None


def test_image_dialog_valid_image(tmp_path, monkeypatch):
    monkeypatch.setattr(
        io_helper_module, "load_dotenv", lambda: None
    )
    monkeypatch.delenv("APP_CONTAINER", raising=False)

    image = tmp_path / "photo.jpg"
    image.write_bytes(b"image")

    class FakeRoot:
        def withdraw(self):
            pass

        def destroy(self):
            pass

    monkeypatch.setattr(tk, "Tk", lambda: FakeRoot())

    monkeypatch.setattr(
        io_helper_module.filedialog,
        "askopenfilename",
        lambda **kwargs: str(image)
    )

    result = IoHelper.read_image_path(lambda prompt: "")

    assert result == str(image)


def test_image_dialog_invalid_extension(tmp_path, monkeypatch):
    monkeypatch.setattr(
        io_helper_module, "load_dotenv", lambda: None
    )
    monkeypatch.delenv("APP_CONTAINER", raising=False)

    invalid_file = tmp_path / "document.txt"
    invalid_file.write_text("test")

    valid_image = tmp_path / "photo.jpg"
    valid_image.write_bytes(b"image")

    class FakeRoot:
        def withdraw(self):
            pass

        def destroy(self):
            pass

    monkeypatch.setattr(tk, "Tk", lambda: FakeRoot())

    selections = iter([
        str(invalid_file),
        str(valid_image)
    ])

    monkeypatch.setattr(
        io_helper_module.filedialog,
        "askopenfilename",
        lambda **kwargs: next(selections)
    )

    result = IoHelper.read_image_path(lambda prompt: "")

    assert result == str(valid_image)


def test_image_dialog_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        io_helper_module, "load_dotenv", lambda: None
    )
    monkeypatch.delenv("APP_CONTAINER", raising=False)

    missing_image = tmp_path / "missing.jpg"

    valid_image = tmp_path / "photo.jpg"
    valid_image.write_bytes(b"image")

    class FakeRoot:
        def withdraw(self):
            pass

        def destroy(self):
            pass

    monkeypatch.setattr(tk, "Tk", lambda: FakeRoot())

    selections = iter([
        str(missing_image),
        str(valid_image)
    ])

    monkeypatch.setattr(
        io_helper_module.filedialog,
        "askopenfilename",
        lambda **kwargs: next(selections)
    )

    result = IoHelper.read_image_path(lambda prompt: "")

    assert result == str(valid_image)


def test_image_dialog_tkinter_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        io_helper_module, "load_dotenv", lambda: None
    )
    monkeypatch.delenv("APP_CONTAINER", raising=False)

    valid_image = tmp_path / "photo.jpg"
    valid_image.write_bytes(b"image")

    class FakeRoot:
        def withdraw(self):
            pass

        def destroy(self):
            pass

    attempts = iter([
        tk.TclError("Window unavailable"),
        FakeRoot()
    ])

    def fake_tk():
        attempt = next(attempts)

        if isinstance(attempt, Exception):
            raise attempt

        return attempt

    monkeypatch.setattr(tk, "Tk", fake_tk)

    monkeypatch.setattr(
        io_helper_module.filedialog,
        "askopenfilename",
        lambda **kwargs: str(valid_image)
    )

    result = IoHelper.read_image_path(lambda prompt: "")

    captured = capsys.readouterr()

    assert "Window unavailable" in captured.out
    assert result == str(valid_image)
