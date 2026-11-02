from datetime import datetime

class AnalysisValidator:
    def __is_valid_ai_result(self, ai_result):
        return (
            isinstance(ai_result, dict)
            and "similarity_analysis" in ai_result
            and isinstance(ai_result["similarity_analysis"], dict)
        )

    def __parse_score_to_float(self, score):
        # Handle scores returned directly as an integer or float.
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            value = float(score)
        elif isinstance(score, str):
            try:
                value = float(score.strip().rstrip("%"))
            except ValueError:
                return None
        else:
            return None
        # Ensure the score is between 0 and 100.
        return value if 0 <= value <= 100 else None

    def validate_analysis(self, ai_result):
        if not self.__is_valid_ai_result(ai_result):
            return "system_failure", "Invalid AI output structure"
        analysis = ai_result.get("similarity_analysis")
        # 3. Extract and validate the similarity score.
        similarity_score = analysis.get("similarity_score")
        score = self.__parse_score_to_float(similarity_score)
        # Reject missing, invalid, or out-of-range scores.
        if score is None:
            return (
                "system_failure",
                f"Invalid or out-of-bounds similarity_score: {similarity_score}",
            )
        # 4. Check if "color_match" exists and is a dictionary with "is_match" key.
        color_data = analysis.get("color_match")
        if isinstance(color_data, dict):
            color_match = color_data.get("is_match")
            if color_match not in ("match", "not match"):
                return "system_failure", "Invalid 'is_match' value in 'color_match'"
        elif isinstance(color_data, str):
            if color_data not in ("match", "not match"):
                return "system_failure", "Invalid 'color_match' value"
            color_match = color_data
        else:
            return "system_failure", "Corrupted or missing 'color_match' data structure"
        # 5. Check if "feature_overlap_match" exists and is a list.
        if not isinstance(analysis.get("feature_overlap_match"), list):
            return "system_failure", "Invalid 'feature_overlap_match' data structure"
        return "valid", score

    def validate_timeline(self, ai_result, lost_report_date):
        if not self.__is_valid_ai_result(ai_result) or not lost_report_date:
            return "unknown"

        try:
            fmt = "%d-%m-%Y"
            lost_date = datetime.strptime(lost_report_date, fmt)
            found_date = datetime.strptime(ai_result["date"], fmt)

            return "impossible_timeline" if found_date < lost_date else "valid"

        except (ValueError, TypeError, KeyError):
            return "unknown"