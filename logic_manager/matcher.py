from .analysis_validator import AnalysisValidator
from .traits import Traits
from .threshold_config import ThresholdConfig
from .rule_manager import RuleManager
# Negative business rules #
from .rule_mismatch_location import LocationMismatchRule
# Positive business rules #
from .rule_match_brand_color import BrandAndColorMatchRule

class Matcher:
    def __init__(self, validator=None):
        self.validator = validator
        self.traits = Traits()
        self.threshold_config = ThresholdConfig()
        self.rule_manager = RuleManager()
        self.rule_manager.add_rule(LocationMismatchRule())
        self.rule_manager.add_rule(BrandAndColorMatchRule())
    
    def apply_rule(self, rule, data):
        if rule.is_satisfied(data):
            return rule.get_score_adjustment()

        return 0.0

    def evaluate_analysis(self, ai_result, lost_report_date=None):
        # Validate the AI output and extract the original similarity score
        validation, similarity_score = self.validator.validate_analysis(ai_result)
        # Stop processing if the AI output is invalid
        if validation == "system_failure":
            return {
                "status": "system_failure",
                "final_composite_score": None,
                "matched_rules_list": [],
                "mismatched_rules_list": [],
                "triggered_rules_list": [],
                "evaluation_summary": "Invalid AI output."
            }
        # Extract and normalize the analysis data
        data = self.traits.get_traits(ai_result, lost_report_date)
        
        time_match = data["time_match"]
        color_match = data["color_match"]
        color_data = data["color_data"]
        material_match = data["material_match"]
        brand_match = data["brand_match"]
        location_match = data["location_match"]
        feature_overlaps = data["feature_overlaps"]
        
        # Initialize lists to track matched and mismatched attributes, as well as triggered business rules
        matched_rules_list, mismatched_rules_list = self.traits.classify_traits(data)
        # Store the triggered business rules for reporting purposes
        triggered_rules_list = []
        # Start with the original similarity score as the base for the final composite score
        final_score = similarity_score
        # Count the number of overlapping features for use in business rule evaluation
        feature_count = len(feature_overlaps)

        # ----------------------------------------------------------------
        # CRITICAL PHYSICAL BOUNDARY CHECKS >> Reject regardless of score
        # ----------------------------------------------------------------
        if time_match == "impossible_timeline":
            triggered_rules_list.append("TEMPORAL_PARADOX_VETO")
            return {
                "status": "match_failure",
                "final_composite_score": 0.0,
                "matched_rules_list": matched_rules_list,
                "mismatched_rules_list": mismatched_rules_list,
                "triggered_rules_list": triggered_rules_list,
                "evaluation_summary": "The found date cannot occur before the lost date."
            }

        # ------------------------------------
        # Negative Business Rules (Penalties)
        # ------------------------------------
        '''
        CORE_VISUAL_MISMATCH_VETO → basically no physical evidence matches
        COLOR_AND_MATERIAL_MISMATCH → two important physical attributes disagree
        LOCATION_MISMATCH → location evidence disagrees
        COLOR_ONLY_MATCH → only colour supports the match
        '''
        
        # 1. WEAKEST PHYSICAL MATCH: No color, no material, and no features match. (Veto rule)
        if color_match == "not match" and material_match == "not match" and feature_count == 0:
            triggered_rules_list.append("CORE_VISUAL_MISMATCH_VETO")
            final_score = min(final_score, 25.0)    # set a low score
        # 2. WEAK PHYSICAL MATCH: Color and material do not match, but there are some features or brand matches. (Penalty rule)
        elif color_match == "not match" and material_match == "not match":
            triggered_rules_list.append("COLOR_AND_MATERIAL_MISMATCH")
            final_score -= 10.0
        
        # 3. LOCATION MISMATCH: The lost and found locations do not match. (Penalty rule)
        if location_match == "not match":
            triggered_rules_list.append("LOCATION_MISMATCH")
            final_score -= 5.0

        # 4. WEAK COLOR MATCH: Only color matches (Penalty rule)
        if color_match == "match" and material_match == "not match" and brand_match == "not match" and feature_count == 0:
            triggered_rules_list.append("COLOR_ONLY_MATCH")
            final_score -= 10.0

        # ----------------------------------
        # Positive Business Rules (Bonuses)
        # ----------------------------------
        positive_rule = None
        positive_bonus = 0.0
        #s
        # 1. EXCELLENT MATCH: All major attributes match, including location, and there are enough overlapping features.
        if color_match == "match" and material_match == "match" and brand_match == "match" and feature_count >= self.min_features_excellent_match and location_match == "match":
            positive_rule = "ALL_MAJOR_ATTRIBUTES_AND_LOCATION_MATCH"
            positive_bonus = 10.0
        
        # 2. STRONG MATCH: All major attributes match, and there are enough overlapping features.
        elif color_match == "match" and material_match == "match" and brand_match == "match" and feature_count >= self.min_features_excellent_match:
            positive_rule = "FOUR_FACTOR_MATCH"
            positive_bonus = 10.0

        # 3. STRONG MATCH: Brand, color, and features match.
        elif brand_match == "match" and color_match == "match" and feature_count >= self.min_features_strong_match:
            positive_rule = "BRAND_COLOR_FEATURE_MATCH"
            positive_bonus = 10.0
        
        # 4. STRONG MATCH: Color, material, and features match.
        elif color_match == "match" and material_match == "match" and feature_count >= self.min_features_strong_match:
            positive_rule = "COLOR_MATERIAL_FEATURE_MATCH"
            positive_bonus = 10.0
        
        # 5. STRONG MATCH: Color, material, and brand match.
        elif color_match == "match" and material_match == "match" and brand_match == "match":
            positive_rule = "COLOR_MATERIAL_BRAND_MATCH"
            positive_bonus = 10.0
            
        # 6. GOOD MATCH: Brand and features match.
        elif brand_match == "match" and feature_count >= self.min_features_strong_match:
            positive_rule = "BRAND_AND_FEATURE_MATCH"
            positive_bonus = 8.0
        
        #7. GOOD MATCH: Brand and color match.
        elif brand_match == "match" and color_match == "match":
            positive_rule = "BRAND_AND_COLOR_MATCH"
            positive_bonus = 7.0
        
        # 8. GOOD MATCH: Brand and material match.
        elif brand_match == "match" and material_match == "match":
            positive_rule = "BRAND_AND_MATERIAL_MATCH"
            positive_bonus = 7.0
        
        # 9. OK MATCH: Color and multiple features match.
        elif color_match == "match" and feature_count >= self.min_features_strong_match:
            positive_rule = "COLOR_AND_MULTIPLE_FEATURES_MATCH"
            positive_bonus = 5.0
        
        # 10. OK MATCH: Material and multiple features match.
        elif material_match == "match" and feature_count >= self.min_features_strong_match:
            positive_rule = "MATERIAL_AND_MULTIPLE_FEATURES_MATCH"
            positive_bonus = 5.0
            
        # 11. OK MATCH: Color and material match.
        elif color_match == "match" and material_match == "match":
            positive_rule = "COLOR_AND_MATERIAL_MATCH"
            positive_bonus = 5.0

        if positive_rule:
            triggered_rules_list.append(positive_rule)
            final_score += positive_bonus

        # ----------------------------
        # Additional Colour Rule
        # ----------------------------
        if isinstance(color_data, dict) and "secondary" in color_data and color_match == "match":
            triggered_rules_list.append("PRIMARY_SECONDARY_COLOR_MATCH")
            final_score += 3.0

        final_score = max(0.0, min(final_score, 100.0))

        # ----------------------------
        # Determine Final Status
        # ----------------------------
        # A visual mismatch veto always causes the match to fail, regardless of the final score.
        if "CORE_VISUAL_MISMATCH_VETO" in triggered_rules_list:
            status = "match_failure"
            evaluation_summary = "The reports have insufficient visual similarity to support a reliable match."
        
        # Strong positive business rules indicate that multiple important attributes support the match.
        elif final_score >= self.high_threshold and positive_rule in (
            "ALL_MAJOR_ATTRIBUTES_AND_LOCATION_MATCH",
            "FOUR_FACTOR_MATCH",
            "BRAND_COLOR_FEATURE_MATCH",
            "COLOR_MATERIAL_FEATURE_MATCH",
            "COLOR_MATERIAL_BRAND_MATCH"
        ):
            status = "RECOMMENDED_MATCH"
            evaluation_summary = "Multiple independent attributes strongly support a potential match."
        
        # A high score without a strong positive rule is still considered a potential match rather than a recommended match.
        elif final_score >= self.high_threshold:
            status = "POTENTIAL_MATCH"
            evaluation_summary = "The reports show a high degree of similarity, but not all key attributes align."
        # Scores within the acceptable range are possible matches, but require further verification.
        elif final_score >= self.reject_threshold:
            status = "POTENTIAL_MATCH"
            evaluation_summary = "The reports show a moderate degree of similarity, but some key attributes do not align."
        # Scores below the rejection threshold are considered too weak to suggest a viable match.
        else:
            status = "LOW_CONFIDENCE_MATCH"
            evaluation_summary = "The similarity metrics are too low to suggest a viable match."

        return {
            "status": status,
            "final_composite_score": final_score,
            "matched_rules_list": matched_rules_list,
            "mismatched_rules_list": mismatched_rules_list,
            "triggered_rules_list": triggered_rules_list,
            "evaluation_summary": evaluation_summary
        }

    # Function to get the best match from a list of AI results based on the final composite score and business rules
    def get_best_match(self, ai_result_list, lost_report_date=None):
        """_summary_
            Function to apply business rules to a list of AI results and determine the best match based on the final composite score.
        Args:
            ai_result_list (list): Top 3 matches returned from AI semantic matching
            lost_report_date (str, optional): The date the lost report was filed. Defaults to None.

        Returns:
            dict: The best matching report and its evaluation details.
        """
        # Store the best matching report and its evaluation.
        # Start with None because no report has been evaluated yet.
        best_report = None
        best_evaluation = None
        
        # Evaluate AI results one by one and keep track of the best match based on the final composite score.
        for ai_result in ai_result_list:
            evaluation = self.evaluate_analysis(ai_result, lost_report_date)
            
            # Ignore reports that could not be processed successfully or were rejected by the visual mismatch veto rule.
            if evaluation["status"] in ("system_failure", "match_failure"):
                continue
            
            # If this is the first valid report, use it as the current best match.
            if best_evaluation is None:
                best_report = ai_result
                best_evaluation = evaluation
                continue
            # Compare the current report's final score with the score of the current best report.
            # Replace the best match if the current report has a higher score.
            if (evaluation["final_composite_score"] > best_evaluation["final_composite_score"]):
                best_report = ai_result
                best_evaluation = evaluation
        # If no valid report was found, return None.
        if best_report is None:
            return None
        # Return the report with the highest final score together with its evaluation details.
        return {"report": best_report, "evaluation": best_evaluation}