class MatchSelector:
    """
    Selects the best matching report from a list of evaluation results.
    """

    STATUS_PRIORITY = {
        "RECOMMENDED_MATCH": 3,
        "POTENTIAL_MATCH": 2,
        "LOW_CONFIDENCE_MATCH": 1
    }

    def get_best_match(self, evaluation_results):
        best_report = None
        best_evaluation = None

        for result in evaluation_results:
            evaluation = result["evaluation"]

            # Skip reports that failed validation or did not qualify as a match.
            if evaluation["status"] in ("system_failure", "match_failure"):
                continue

            if best_evaluation is None:
                best_report = result["report"]
                best_evaluation = evaluation
                continue

            # Compare classification priority first.
            current_priority = self.STATUS_PRIORITY.get(
                evaluation["status"], 0
            )
            best_priority = self.STATUS_PRIORITY.get(
                best_evaluation["status"], 0
            )

            # If classification is equal, compare scores.
            if (
                current_priority > best_priority
                or (
                    current_priority == best_priority
                    and evaluation["final_composite_score"]
                    > best_evaluation["final_composite_score"]
                )
            ):
                best_report = result["report"]
                best_evaluation = evaluation

        if best_report is None:
            return None

        return {
            "report": best_report,
            "evaluation": best_evaluation
        }