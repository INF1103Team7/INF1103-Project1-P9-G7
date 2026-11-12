# Print menu class

from collections.abc import Callable, Iterable, Mapping

from .formatting import Format


# Centralize terminal output for menus, reports, and status messages
class PrintMenu:
    @staticmethod
    def write(message: object = "") -> None:
        """_summary_
            Helper method to print messages to the terminal. Can be used for printing menus, reports, and status messages.
        Args:
            message (object, optional): The message to print. Defaults to "".
        """
        print(message)

    @classmethod
    def choices(cls, title: str, choices: tuple[str, ...]) -> None:
        """_summary_
            Displays a list of choices to the user in a formatted manner.
        Args:
            title (str): The title of the choices section.
            choices (tuple[str, ...]): A tuple of strings representing the choices to display.
        """
        cls.write(title)
        for number, choice in enumerate(choices, start=1):
            cls.write(f"{number}. {choice.title()}")

    @classmethod
    def navigation(cls, include_back: bool = True) -> None:
        """_summary_
            Displays navigation options to the user, including the option to go back to the previous step or return to the main menu.
        Args:
            include_back (bool, optional): Whether to include the 'go back' option. Defaults to True.
        """
        if include_back:
            cls.write("B. Go back to the previous step.")
        cls.write("M. Go back to the Main Menu")

    @classmethod
    def section(cls, title: str, width: int, *, leading_newline: bool = True,) -> None:
        """_summary_
            Helper method to display a section title with a specified width and optional leading newline for better readability.
        Args:
            title (str): The title of the section to display.
            width (int): The width of the section title, which determines how many '=' characters will be printed above and below the title.
            leading_newline (bool, optional): Whether to include a leading newline before the section title. Defaults to True.
        """
        prefix = "\n" if leading_newline else ""
        cls.write(f"{prefix}{'=' * width}")
        cls.write(title)
        cls.write("=" * width)

    @classmethod
    def display_summary(cls, records: Iterable[Mapping[str, object]]) -> None:
        """_summary_
            Displays a summary of lost and found reports in a formatted manner.
        Args:
            records (Iterable[Mapping[str, object]]): An iterable of dictionaries, each representing a report with its details.
        """
        cls.write("\nLost-and-Found Summary")
        cls.write("======================")
        cls.write(Format.records(records))

    @classmethod
    def best_match(cls, evaluation: Mapping[str, object]) -> None:
        """_summary_
            Displays the best match found from the database.
        Args:
            evaluation (Mapping[str, object]): A mapping containing the evaluation details of the best match.
        """
        cls.write("[+] Best match found from database:")
        cls.write(f"Verdict: {evaluation.get('status')}")
        cls.write(
            "Final score after applying business rules: "
            f"{evaluation.get('final_composite_score')}/100"
        )
        matched_rules = evaluation.get("matched_rules_list")
        mismatched_rules = evaluation.get("mismatched_rules_list")
        cls.write(
            "Matched rules: "
            f"{', '.join(matched_rules) if matched_rules else 'None'}"
        )
        cls.write(
            "Mismatched rules: "
            f"{', '.join(mismatched_rules) if mismatched_rules else 'None'}"
        )
        cls.write(f"Summary: {evaluation.get('evaluation_summary')}")

    @classmethod
    def confirm_best_match(cls, best_match: Mapping[str, object], input_function: Callable[[str], str] = input) -> bool:
        """_summary_
            Function to confirm the best match found from the database with the user.
        Args:
            best_match (Mapping[str, object]): A mapping containing the details of the best match report.
            input_function (Callable[[str], str], optional): The function to use for user input. Defaults to input.

        Returns:
            bool: _description_
        """
        evaluation = best_match.get("evaluation")
        if not isinstance(evaluation, Mapping):
            return print("[!] Error: The best match must include an evaluation mapping.")
        cls.best_match(evaluation)

        while True:
            resolve = input_function(
                "Is this a match for the item you have lost? (yes/no): "
            ).strip().lower()
            if resolve in {"yes", "y"}:
                return True
            if resolve in {"no", "n"}:
                return False
            cls.write("Please enter 'yes' or 'no'.")

    @classmethod
    def configure_threshhold(cls, input_function: Callable[[str], str] = input) -> tuple[int, int, int, int, bool]:
        """_summary_
            Function to configure AI semantic matching thresholds with user input.
        Args:
            input_function (Callable[[str], str], optional): The function to use for user input. Defaults to input.

        Returns:
            tuple[int, int, int, int, bool]: A tuple containing the configured thresholds.
        """
        while True:
            cls.write("\nConfigurable AI semantic matching thresholds")
            cls.write("=============================================")
            cls.write("1. Reject threshold: The minimum similarity score below which a match is rejected.")
            cls.write("2. High threshold: The minimum similarity score above which a match is considered high confidence.")
            cls.write("3. Minimum feature overlap for strong match: The minimum number of overlapping features required for a strong match.")
            cls.write("4. Minimum feature overlap for excellent match: The minimum number of overlapping features required for an excellent match.")
            cls.write("5. Consider location in matching: Whether to consider the location of the lost item in the matching process.")
            
            try:
                reject = int(input_function("\nEnter the reject threshold (0-100), default: 50: ").strip())
                high = int(input_function("Enter the high threshold (0-100) default: 80: ").strip())
                min_strong = int(input_function("Enter the minimum feature overlap for strong match (1 or higher) default: 2: ").strip())
                min_excellent = int(input_function("Enter the minimum feature overlap for excellent match (1 or higher) default: 3: ").strip())
                consider_location = input_function("Consider location in matching? (yes/no) default: yes: ").strip().lower()

                if consider_location in {"yes", "y"}:
                    consider_location = True
                elif consider_location in {"no", "n"}:
                    consider_location = False
                else:
                    cls.write("Invalid input for location consideration. Please enter 'yes' or 'no'.")
                    continue

                finished = input_function("\nFinished configuration? (yes/no): ").strip().lower()
                if finished in {"yes", "y"}:
                    break
                elif finished in {"no", "n"}:
                    continue
                else:
                    cls.write("Please enter 'yes' or 'no'.")
            except Exception as e:
                cls.write(f"[!] Error in configuration: {e}")
                continue
        cls.write("\n[+] Configuration complete.")
        return reject, high, min_strong, min_excellent, consider_location
