# analysis validator class

from datetime import datetime


class AnalysisValidator:
    """
    Validates the structure and contents of AI-generated analysis results.

    Ensures that similarity scores, matching attributes and reported dates are in the expected format before further evaluation.
    """

    def __is_valid_ai_result(self, ai_result: dict) -> bool:
        # Check that the AI result is a dictionary containing a valid similarity_analysis dictionary.
        return (
            isinstance(ai_result, dict)
            and "similarity_analysis" in ai_result
            and isinstance(ai_result["similarity_analysis"], dict)
        )

    def __parse_score_to_float(self, score: any) -> float:
        # Handle scores returned directly as an integer or float.
        # Boolean values are excluded because bool is a subclass of int in Python.
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            value = float(score)

        # Convert string-based scores into floating-point numbers.
        # Remove surrounding whitespace and an optional percentage symbol.
        elif isinstance(score, str):
            try:
                value = float(score.strip().rstrip("%"))
            except ValueError:
                return None
        else:
            return None

        # Ensure the converted score is within the accepted range of 0 to 100.
        return value if 0 <= value <= 100 else None

    def validate_analysis(self, ai_result: dict) -> tuple[str, float]:
        """
        Validate the structure and matching information in an AI result.

        Returns:
            A tuple containing the validation status and similarity score or an error message if validation fails.
        """

        # Check whether the overall AI result has the expected structure.
        if not self.__is_valid_ai_result(ai_result):
            return "system_failure", "Invalid AI output structure"

        analysis = ai_result.get("similarity_analysis")

        # Extract and validate the similarity score.
        similarity_score = analysis.get("similarity_score")
        score = self.__parse_score_to_float(similarity_score)

        # Reject missing, invalid or out-of-range similarity scores.
        if score is None:
            return (
                "system_failure",
                f"Invalid or out-of-bounds similarity_score: {similarity_score}",
            )

        # Check that colour matching information has an accepted structure.
        color_data = analysis.get("color_match")

        # If colour data is a dictionary, validate its "is_match" value.
        if isinstance(color_data, dict):
            color_match = color_data.get("is_match")

            if color_match not in ("match", "not match"):
                return "system_failure", "Invalid 'is_match' value in 'color_match'"

        # If colour data is a string, validate its matching value directly.
        elif isinstance(color_data, str):
            if color_data not in ("match", "not match"):
                return "system_failure", "Invalid 'color_match' value"

            color_match = color_data

        # Reject missing or incorrectly structured colour information.
        else:
            return "system_failure", "Corrupted or missing 'color_match' data structure"

        # Ensure feature_overlap_match is provided as a list.
        if not isinstance(analysis.get("feature_overlap_match"), list):
            return "system_failure", "Invalid 'feature_overlap_match' data structure"

        # Return the successful validation status and converted score.
        return "valid", score

    def validate_timeline(self, ai_result: dict, lost_report_date: str) -> str:
        """
        Check whether the found report date is chronologically valid compared with the lost report date.
        """

        # Return unknown if the AI result is invalid or no lost date is provided.
        if not self.__is_valid_ai_result(ai_result) or not lost_report_date:
            return "unknown"

        try:
            # Define the expected date format: day-month-year.
            fmt = "%d-%m-%Y"

            # Convert both date strings into datetime objects for comparison.
            lost_date = datetime.strptime(lost_report_date, fmt)
            found_date = datetime.strptime(ai_result["date"], fmt)

            # A found report dated before the lost report is an impossible timeline.
            return "impossible_timeline" if found_date < lost_date else "valid"

        # Handle incorrectly formatted dates, missing date keys or invalid types.
        except (ValueError, TypeError, KeyError):
            return "unknown"