class MatchSelector:
    """
    Selects the best matching report from a list of evaluation results.
    """

    def get_best_match(self, evaluation_results):
        # Initialise the variables to store the best report and its evaluation.
        best_report = None
        best_evaluation = None

        # Go through each report and its corresponding evaluation.
        for result in evaluation_results:
            evaluation = result["evaluation"]

            # Skip reports that failed validation or did not qualify as a match.
            if evaluation["status"] in ("system_failure", "match_failure"):
                continue

            # Select the first valid result, or replace it if a higher score is found.
            if (
                best_evaluation is None
                or evaluation["final_composite_score"]
                > best_evaluation["final_composite_score"]
            ):
                best_report = result["report"]
                best_evaluation = evaluation

        # Return None if no valid matching report was found.
        if best_report is None:
            return None

        # Return the report together with its evaluation details.
        return {
            "report": best_report,
            "evaluation": best_evaluation
        }