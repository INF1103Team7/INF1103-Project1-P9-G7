class MatchSelector:

    def get_best_match(self, evaluation_results):
        best_report = None
        best_evaluation = None

        for result in evaluation_results:
            evaluation = result["evaluation"]

            if evaluation["status"] in ("system_failure", "match_failure"):
                continue

            if (
                best_evaluation is None
                or evaluation["final_composite_score"]
                > best_evaluation["final_composite_score"]
            ):
                best_report = result["report"]
                best_evaluation = evaluation

        if best_report is None:
            return None

        return {
            "report": best_report,
            "evaluation": best_evaluation
        }