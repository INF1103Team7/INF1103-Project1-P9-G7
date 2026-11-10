from typing import Callable, Iterable, Mapping

from .formatting import Format


class PrintMenu:
    """Centralize terminal output for menus, reports, and status messages."""

    @staticmethod
    def write(message: object = "") -> None:
        print(message)

    @classmethod
    def choices(cls, title: str, choices: tuple[str, ...]) -> None:
        cls.write(title)
        for number, choice in enumerate(choices, start=1):
            cls.write(f"{number}. {choice.title()}")

    @classmethod
    def navigation(cls, include_back: bool = True) -> None:
        if include_back:
            cls.write("B. Go back to the previous step.")
        cls.write("M. Go back to the Main Menu")

    @classmethod
    def section(
        cls,
        title: str,
        width: int,
        *,
        leading_newline: bool = True,
    ) -> None:
        prefix = "\n" if leading_newline else ""
        cls.write(f"{prefix}{'=' * width}")
        cls.write(title)
        cls.write("=" * width)

    @classmethod
    def display_summary(cls, records: Iterable[Mapping[str, object]]) -> None:
        cls.write("\nLost-and-Found Summary")
        cls.write("======================")
        cls.write(Format.records(records))

    @classmethod
    def best_match(cls, evaluation: Mapping[str, object]) -> None:
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
    def confirm_best_match(
        cls,
        best_match: Mapping[str, object],
        input_function: Callable[[str], str] = input
    ) -> bool:
        evaluation = best_match.get("evaluation")
        if not isinstance(evaluation, Mapping):
            raise ValueError("The best match must include an evaluation mapping.")
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
    def configure_threshhold(cls, input_function: Callable[[str], str] = input):
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
        cls.write("[+] Configuration complete.")
        return reject, high, min_strong, min_excellent, consider_location
