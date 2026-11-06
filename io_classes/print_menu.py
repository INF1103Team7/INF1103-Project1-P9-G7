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
        input_function: Callable[[str], str] = input,
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
