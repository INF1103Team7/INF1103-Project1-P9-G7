# logic manager file to apply business rules to the AI output and determine the best match for lost and found reports..
from logic_classes.match_selector import MatchSelector
from logic_classes.matcher import Matcher


class LogicManager:
    def __init__(self, threshold_config=None):
        # Responsible for evaluating individual AI results.
        self.matcher = Matcher(threshold_config=threshold_config)

        # Responsible for selecting the best evaluation.
        self.match_selector = MatchSelector()

    def get_best_match(self, ai_result_list: list, lost_report_date=None) -> dict:
        """
        Evaluate AI results and return the best valid match.

        Args:
            ai_result_list (list): AI semantic matching results.
            lost_report_date (str, optional): Date the lost report was filed.

        Returns:
            dict or None: Best report and its evaluation details.
        """

        evaluation_results = []

        # 1. Evaluate each AI result individually
        for ai_result in ai_result_list:

            evaluation = self.matcher.evaluate_analysis(
                ai_result,
                lost_report_date
            )

            # Store the original report together with its evaluation.
            evaluation_results.append({
                "report": ai_result,
                "evaluation": evaluation
            })

        # 2. Select the best valid match.
        best_match = self.match_selector.get_best_match(
            evaluation_results
        )

        # 3. Return the selected result..
        return best_match
