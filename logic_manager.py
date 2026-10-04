import json
from datetime import datetime

# ============================================================
# GLOBAL BUSINESS CONSTANTS
# ============================================================

# Minimum final score required for a match to have moderate confidence.
REJECT_THRESHOLD = 50.0

# Final scores at or above this value are considered high confidence.
HIGH_THRESHOLD = 80.0

# Minimum number of matching features required for a strong
# multi-attribute match rule.
MIN_FEATURES_STRONG_MATCH = 2

# Minimum number of matching features required for an
# excellent multi-attribute match rule.
MIN_FEATURES_EXCELLENT_MATCH = 3


def parse_score_to_float(score):
    """Convert the AI similarity_score into a float between 0 and 100.

    The AI may return the score as:
    - a % string: "85%" (expected)
    - an integer or float: 85 / 85.0
    - a string: "85"

    Valid score: Returns the score as a float.
    Invalid score: Returns None.
    Used by: validate_analysis()"""
    # Handle scores returned directly as an integer or float.
    if isinstance(score, (int, float)) and not isinstance(score, bool):
        # Reject numeric scores outside the valid 0-100 range.
        if 0 <= score <= 100:
            return float(score)

        return None
    # Reject values that are not strings, integers, or floats.
    if not isinstance(score, str):
        return None
    # Remove whitespace and the optional "%" symbol.
    score_clean = score.strip().rstrip("%")
    try:
        value = float(score_clean)
        # Reject numeric values outside the valid 0-100 range.
        if 0 <= value <= 100:
            return value
    # float() raises ValueError when the string is not numeric.
    except ValueError:
        pass

    return None

def validate_analysis(ai_result):
    '''
    Validate the minimum structure required from the AI output.

    Checks:
    1. The overall AI output is a dictionary.
    2. similarity_analysis exists and is a dictionary.
    3. similarity_score exists and is between 0 and 100.
    4. color_match exists and contains the required is_match key.
    5. feature_overlap_match exists and is a list.

    Valid: Returns ("valid", similarity_score).
    Invalid: Returns ("system_failure", error_message).
    Used by: evaluate_analysis()'''

    # 1. The overall AI result must be a dictionary.
    if not isinstance(ai_result, dict):
        return "system_failure", \
            "AI output structure is not a dictionary"

    # 2. Extract similarity_analysis; If it is missing, .get() returns None.
    analysis = ai_result.get("similarity_analysis")

    # similarity_analysis must be a dictionary because the remaining logic expects to access its keys.
    if not isinstance(analysis, dict):
        return "system_failure", "Missing or invalid 'similarity_analysis' object"

    # 3. Extract and validate the similarity score.
    similarity_score = analysis.get("similarity_score")

    score = parse_score_to_float(similarity_score)

    # Reject missing, invalid, or out-of-range scores.
    if score is None:
        return "system_failure", f"Invalid or out-of-bounds similarity_score: {similarity_score}"
    # 4. Check if "color_match" exists and is a dictionary with "is_match" key.
    color_data = analysis.get("color_match")
    if isinstance(color_data, dict):
        # "is_match" is required; "primary" and "secondary" are optional.
        color_match = color_data.get("is_match")
        if color_match not in ("match", "not match"):
            return "system_failure", "Invalid 'is_match' value in 'color_match'"
    elif isinstance(color_data, str):
        # The AI may also return the older/simple string format.
        if color_data not in ("match", "not match"):
            return "system_failure", "Invalid 'color_match' value"
        color_match = color_data
    else:
        # Reject missing, None, or other invalid data types.
        return "system_failure", "Corrupted or missing 'color_match' data structure"
    # 5. Check if "feature_overlap_match" exists and is a list.
    feature_overlaps = analysis.get("feature_overlap_match")
    if not isinstance(feature_overlaps, list):
        return "system_failure", "Invalid 'feature_overlap_match' data structure"
    
    return "valid", score

def get_analysis_data(ai_result, lost_report_date=None):
    '''
    Extract and normalize the values.

    Missing optional AI fields are given safe default values:
    - match fields default to "not match"
    - feature overlaps default to an empty list
    - invalid dates default to "unknown"

    The function also checks whether the found report date occurred before the lost report date.

    Returns: A dictionary containing the normalized analysis data.
    Used by: evaluate_analysis()'''

    # similarity_analysis has already been validated by validate_analysis() before this function is called.
    analysis = ai_result["similarity_analysis"]
    
    # If keys are missing, the .get() method will return "not match" for match fields and an empty list [] for feature overlaps.
    # --------------------------------------------------------
    # 1. Extract colour match information
    # --------------------------------------------------------
    color_data = analysis.get("color_match", "not match")
    if isinstance(color_data, dict):
        color_match = color_data.get("is_match", "not match")
    else:
        # Fallback for older/simple AI output where color_match may already be a string such as "match".
        color_match = color_data
    # --------------------------------------------------------
    # 2. Extract other matching attributes
    # --------------------------------------------------------
    material_match = analysis.get("material_match", "not match")
    brand_match = analysis.get("brand_match", "not match")
    location_match = analysis.get("location_match", "not match")
    feature_overlaps = analysis.get("feature_overlap_match", [])

    # --------------------------------------------------------
    # Validate the report timeline
    # --------------------------------------------------------
    # Default to "unknown" when the dates cannot be checked.
    time_match = "unknown"
    # Only perform the chronological check when both dates are available.
    if lost_report_date and "date" in ai_result:

        try:
            fmt = "%d-%m-%Y"

            # Convert both date strings into datetime objects.
            lost_dt = datetime.strptime(lost_report_date, fmt)
            found_dt = datetime.strptime(ai_result["date"], fmt)

            # A found report cannot logically occur before the item was reported lost.
            if found_dt < lost_dt:
                time_match = "impossible_timeline"
            else:
                time_match = "valid"

        # Handle incorrectly formatted or incorrectly typed dates.
        except (ValueError, TypeError):
            time_match = "unknown"

    return {
        "color_match": color_match,
        "color_data": color_data,
        "material_match": material_match,
        "brand_match": brand_match,
        "location_match": location_match,
        "feature_overlaps": feature_overlaps,
        "time_match": time_match
    }

def classify_traits(data):
    ''' Classify each item's attribute as either matched or mismatched.

    The attributes checked are:
    - colour
    - material
    - brand
    - location
    - identifying features

    Returns: a tuple of two lists of attributes: (matched, mismatched)
    Used by: evaluate_analysis()'''

    matched = []
    mismatched = []

    # Store the individual attributes that need to be classified.
    traits = {
        "color": data["color_match"],
        "material": data["material_match"],
        "brand": data["brand_match"],
        "location": data["location_match"],
    }

    # Classify each attribute based on whether the AI marked it as a match.
    for trait, result in traits.items():

        if result == "match":
            matched.append(trait)
        else:
            mismatched.append(trait)

    # Features are considered a match when at least one overlapping feature exists.
    if len(data["feature_overlaps"]) > 0:
        matched.append("features")
    else:
        mismatched.append("features")

    return matched, mismatched

def evaluate_analysis(ai_result, lost_report_date=None):
    ''' Evaluate one AI-generated report using the business rules.

    Process:
    1. Validate the AI output.
    2. Extract and normalize the analysis data.
    3. Classify matched and mismatched attributes.
    4. Apply negative business rules.
    5. Apply positive business rules.
    6. Calculate the final composite score.
    7. Determine the final match status.

    Returns: A dictionary containing the final score, status, matched attributes, mismatched attributes, triggered rules, and evaluation summary.
    Used by: get_best_match()'''
    # Validate the AI output and extract the original similarity score
    validation, similarity_score = validate_analysis(ai_result)
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
    data = get_analysis_data(ai_result, lost_report_date)
    
    time_match = data["time_match"]
    color_match = data["color_match"]
    color_data = data["color_data"]
    material_match = data["material_match"]
    brand_match = data["brand_match"]
    location_match = data["location_match"]
    feature_overlaps = data["feature_overlaps"]
    
    # Initialize lists to track matched and mismatched attributes, as well as triggered business rules
    matched_rules_list, mismatched_rules_list = classify_traits(data)
    # Store the triggered business rules for reporting purposes
    triggered_rules_list = []
    # Start with the original similarity score as the base for the final composite score
    final_score = similarity_score
    # Count the number of overlapping features for use in business rule evaluation
    feature_count = len(feature_overlaps)

    # ----------------------------
    # CRITICAL PHYSICAL BOUNDARY CHECKS >> Reject regardless of score
    # ----------------------------
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

    # ----------------------------
    # Negative Business Rules (Penalties)
    # ----------------------------
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

    # ----------------------------
    # Positive Business Rules (Bonuses)
    # ----------------------------
    positive_rule = None
    positive_bonus = 0.0
    
    # 1. EXCELLENT MATCH: All major attributes match, including location, and there are enough overlapping features.
    if color_match == "match" and material_match == "match" and brand_match == "match" and feature_count >= MIN_FEATURES_EXCELLENT_MATCH and location_match == "match":
        positive_rule = "ALL_MAJOR_ATTRIBUTES_AND_LOCATION_MATCH"
        positive_bonus = 10.0
    
    # 2. STRONG MATCH: All major attributes match, and there are enough overlapping features.
    elif color_match == "match" and material_match == "match" and brand_match == "match" and feature_count >= MIN_FEATURES_EXCELLENT_MATCH:
        positive_rule = "FOUR_FACTOR_MATCH"
        positive_bonus = 10.0

    # 3. STRONG MATCH: Brand, color, and features match.
    elif brand_match == "match" and color_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
        positive_rule = "BRAND_COLOR_FEATURE_MATCH"
        positive_bonus = 10.0
    
    # 4. STRONG MATCH: Color, material, and features match.
    elif color_match == "match" and material_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
        positive_rule = "COLOR_MATERIAL_FEATURE_MATCH"
        positive_bonus = 10.0
    
    # 5. STRONG MATCH: Color, material, and brand match.
    elif color_match == "match" and material_match == "match" and brand_match == "match":
        positive_rule = "COLOR_MATERIAL_BRAND_MATCH"
        positive_bonus = 10.0
        
    # 6. GOOD MATCH: Brand and features match.
    elif brand_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
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
    elif color_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
        positive_rule = "COLOR_AND_MULTIPLE_FEATURES_MATCH"
        positive_bonus = 5.0
    
    # 10. OK MATCH: Material and multiple features match.
    elif material_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
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
    elif final_score >= HIGH_THRESHOLD and positive_rule in (
        "ALL_MAJOR_ATTRIBUTES_AND_LOCATION_MATCH",
        "FOUR_FACTOR_MATCH",
        "BRAND_COLOR_FEATURE_MATCH",
        "COLOR_MATERIAL_FEATURE_MATCH",
        "COLOR_MATERIAL_BRAND_MATCH"
    ):
        status = "RECOMMENDED_MATCH"
        evaluation_summary = "Multiple independent attributes strongly support a potential match."
    
    # A high score without a strong positive rule is still considered a potential match rather than a recommended match.
    elif final_score >= HIGH_THRESHOLD:
        status = "POTENTIAL_MATCH"
        evaluation_summary = "The reports show a high degree of similarity, but not all key attributes align."
    # Scores within the acceptable range are possible matches, but require further verification.
    elif final_score >= REJECT_THRESHOLD:
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

def get_best_match(ai_result_list, lost_report_date=None):
    # Store the best matching report and its evaluation.
    # Start with None because no report has been evaluated yet.
    best_report = None
    best_evaluation = None
    
    # Evaluate AI results one by one and keep track of the best match based on the final composite score.
    for ai_result in ai_result_list:
        evaluation = evaluate_analysis(ai_result, lost_report_date)
        
        '''
        print("\n--- EVALUATION ---")
        print("Status:", evaluation["status"])
        print("Score:", evaluation["final_composite_score"])
        print("Triggered rules:", evaluation["triggered_rules_list"])'''
        
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
