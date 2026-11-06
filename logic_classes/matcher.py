from .analysis_validator import AnalysisValidator
from .traits import Traits
from .threshold_config import ThresholdConfig
from .rule_manager import RuleManager

class Matcher:
    """
    Coordinates the validation, trait extraction and business rule evaluation processes to determine how well two reports match.
    """

    def __init__(self, validator=None, threshold_config=None):

        self.validator = (
            validator if validator is not None else AnalysisValidator()
        )

        self.traits = Traits(self.validator)

        self.threshold_config = (
            threshold_config if threshold_config is not None else ThresholdConfig()
        )

        self.rule_manager = RuleManager(self.threshold_config)

    def handle_temporal_paradox(self, data, matched_rules_list, mismatched_rules_list):
        # Check whether the found date occurs before the reported lost date.
        if data["time_match"] == "impossible_timeline":
            # Immediately reject the match because the timeline is impossible.
            return {
                "status": "match_failure",
                "final_composite_score": 0.0,
                "matched_rules_list": matched_rules_list,
                "mismatched_rules_list": mismatched_rules_list,
                "triggered_rules_list": ["TEMPORAL_PARADOX_VETO"],
                "evaluation_summary": "The found date cannot occur before the lost date."
            }

        # Return None when no temporal paradox is detected.
        return None

    def evaluate_rules(self, data, similarity_score, matched_rules_list, mismatched_rules_list):
        # Delegate the evaluation of registered business rules to RuleManager.
        evaluation = self.rule_manager.evaluate(data, similarity_score)

        # Extract the results returned by RuleManager.
        final_score = evaluation["final_score"]
        triggered_rules_list = evaluation["triggered_rules_list"]
        veto_triggered = evaluation["veto_triggered"]
        positive_rule = evaluation["positive_rule"]

        # Retrieve the configured thresholds.
        high_threshold = self.threshold_config.high_threshold
        reject_threshold = self.threshold_config.reject_threshold

        # Determine the final matching status based on the score and triggered rules.
        if veto_triggered:
            status = "match_failure"
            evaluation_summary = "The reports have insufficient visual similarity to support a reliable match."

        elif final_score >= high_threshold and positive_rule in (
            "ALL_MAJOR_ATTRIBUTES_AND_LOCATION_MATCH",
            "FOUR_FACTOR_MATCH",
            "BRAND_COLOR_FEATURE_MATCH",
            "COLOR_MATERIAL_FEATURE_MATCH",
            "COLOR_MATERIAL_BRAND_MATCH"
        ):
            status = "RECOMMENDED_MATCH"
            evaluation_summary = "Multiple independent attributes strongly support a potential match."

        elif final_score >= high_threshold:
            status = "POTENTIAL_MATCH"
            evaluation_summary = "The reports show a high degree of similarity, but not all key attributes align."

        elif final_score >= reject_threshold:
            status = "POTENTIAL_MATCH"
            evaluation_summary = "The reports show a moderate degree of similarity, but some key attributes do not align."

        else:
            status = "LOW_CONFIDENCE_MATCH"
            evaluation_summary = "The similarity metrics are too low to suggest a viable match."

        # Return the final evaluation details.
        return {
            "status": status,
            "final_composite_score": final_score,
            "triggered_rules_list": triggered_rules_list,
            "matched_rules_list": matched_rules_list,
            "mismatched_rules_list": mismatched_rules_list,
            "evaluation_summary": evaluation_summary
        }

    def evaluate_analysis(self, ai_result, lost_report_date=None):
        # Validate the AI-generated result and retrieve its similarity score.
        validation, similarity_score = self.validator.validate_analysis(ai_result)

        # Stop the evaluation if the AI output is invalid.
        if validation == "system_failure":
            return {
                "status": "system_failure",
                "final_composite_score": None,
                "matched_rules_list": [],
                "mismatched_rules_list": [],
                "triggered_rules_list": [],
                "evaluation_summary": "Invalid AI output."
            }

        # Extract the matching attributes from the AI result.
        data = self.traits.get_traits(ai_result, lost_report_date)

        # Classify the extracted attributes into matched and mismatched lists.
        matched_rules_list, mismatched_rules_list = (
            self.traits.classify_traits(data)
        )

        # Check whether the reported dates create an impossible timeline.
        temporal_result = self.handle_temporal_paradox(
            data,
            matched_rules_list,
            mismatched_rules_list
        )

        # Return immediately if an impossible timeline is detected.
        if temporal_result is not None:
            return temporal_result

        # Evaluate the registered business rules if the result passes validation.
        return self.evaluate_rules(
            data,
            similarity_score,
            matched_rules_list,
            mismatched_rules_list
        )