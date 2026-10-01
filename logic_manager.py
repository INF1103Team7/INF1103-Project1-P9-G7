import json
from datetime import datetime

# Global Business Constants
REJECT_THRESHOLD = 50.0
HIGH_THRESHOLD = 80.0

MIN_FEATURES_STRONG_MATCH = 2
MIN_FEATURES_EXCELLENT_MATCH = 3


def parse_score_to_float(score):
    if not isinstance(score, str) or not score.endswith("%"):
        return None
    try:
        value = float(score[:-1])
        if 0 <= value <= 100:
            return value
    except ValueError:
        pass
    return None


def validate_analysis(ai_result):
    if not isinstance(ai_result, dict):
        return "system_failure", None

    analysis = ai_result.get("similarity_analysis")
    if not isinstance(analysis, dict):
        return "system_failure", None

    similarity_score = analysis.get("similarity_score")
    score = parse_score_to_float(similarity_score)

    if score is None:
        return "system_failure", None

    return "valid", score


def get_analysis_data(ai_result, lost_report_date=None):
    analysis = ai_result["similarity_analysis"]

    color_data = analysis.get("color_match", "not match")
    if isinstance(color_data, dict):
        color_match = color_data.get("is_match", "not match")
    else:
        color_match = color_data

    material_match = analysis.get("material_match", "not match")
    brand_match = analysis.get("brand_match", "not match")
    location_match = analysis.get("location_match", "not match")
    feature_overlaps = analysis.get("feature_overlap_match", [])

    if not isinstance(feature_overlaps, list):
        feature_overlaps = []

    # Calculate temporal chronological validity
    time_match = "unknown"
    if lost_report_date and "date" in ai_result:
        try:
            fmt = "%d-%m-%Y"
            lost_dt = datetime.strptime(lost_report_date, fmt)
            found_dt = datetime.strptime(ai_result["date"], fmt)
            
            if found_dt < lost_dt:
                time_match = "impossible_timeline"
            else:
                time_match = "valid"
        except ValueError:
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
    matched = []
    mismatched = []

    traits = {
        "color": data["color_match"],
        "material": data["material_match"],
        "brand": data["brand_match"],
        "location": data["location_match"],
    }

    for trait, result in traits.items():
        if result == "match":
            matched.append(trait)
        else:
            mismatched.append(trait)

    if len(data["feature_overlaps"]) > 0:
        matched.append("features")
    else:
        mismatched.append("features")

    return matched, mismatched


def evaluate_analysis(ai_result, lost_report_date=None):
    # Validate the AI output and extract the original similarity score
    validation, similarity_score = validate_analysis(ai_result)

    if validation == "system_failure":
        return {
            "status": "system_failure",
            "final_composite_score": None,
            "matched_rules_list": [],
            "mismatched_rules_list": [],
            "triggered_rules_list": [],
            "evaluation_summary": "Invalid AI output."
        }

    data = get_analysis_data(ai_result, lost_report_date)
    
    time_match = data["time_match"]
    color_match = data["color_match"]
    color_data = data["color_data"]
    material_match = data["material_match"]
    brand_match = data["brand_match"]
    location_match = data["location_match"]
    feature_overlaps = data["feature_overlaps"]

    matched_rules_list, mismatched_rules_list = classify_traits(data)
    triggered_rules_list = []
    final_score = similarity_score
    feature_count = len(feature_overlaps)

    # ----------------------------
    # CRITICAL PHYSICAL BOUNDARY CHECKS
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
    if color_match == "not match" and material_match == "not match" and feature_count == 0:
        triggered_rules_list.append("CORE_VISUAL_MISMATCH_VETO")
        final_score = min(final_score, 25.0)
    elif color_match == "not match" and material_match == "not match":
        triggered_rules_list.append("COLOR_AND_MATERIAL_MISMATCH")
        final_score -= 10.0

    if location_match == "not match":
        triggered_rules_list.append("LOCATION_MISMATCH")
        final_score -= 5.0

    if color_match == "match" and material_match == "not match" and feature_count == 0:
        if brand_match == "not match":
            triggered_rules_list.append("WEAK_COLOR_MATCH")
            final_score -= 10.0
        else:
            triggered_rules_list.append("COLOR_ONLY_MATCH")
            final_score -= 5.0

    if brand_match == "not match" and material_match == "not match" and feature_count == 0:
        triggered_rules_list.append("NO_SUPPORTING_ATTRIBUTES")
        final_score -= 10.0

    # ----------------------------
    # Positive Business Rules (Bonuses)
    # ----------------------------
    positive_rule = None
    positive_bonus = 0.0

    if color_match == "match" and material_match == "match" and brand_match == "match" and feature_count >= MIN_FEATURES_EXCELLENT_MATCH and location_match == "match":
        positive_rule = "ALL_MAJOR_ATTRIBUTES_AND_LOCATION_MATCH"
        positive_bonus = 10.0
    elif color_match == "match" and material_match == "match" and brand_match == "match" and feature_count >= MIN_FEATURES_EXCELLENT_MATCH:
        positive_rule = "FOUR_FACTOR_MATCH"
        positive_bonus = 10.0
    elif brand_match == "match" and color_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
        positive_rule = "BRAND_COLOR_FEATURE_MATCH"
        positive_bonus = 10.0
    elif color_match == "match" and material_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
        positive_rule = "COLOR_MATERIAL_FEATURE_MATCH"
        positive_bonus = 10.0
    elif color_match == "match" and material_match == "match" and brand_match == "match":
        positive_rule = "COLOR_MATERIAL_BRAND_MATCH"
        positive_bonus = 10.0
    elif brand_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
        positive_rule = "BRAND_AND_FEATURE_MATCH"
        positive_bonus = 8.0
    elif brand_match == "match" and color_match == "match":
        positive_rule = "BRAND_AND_COLOR_MATCH"
        positive_bonus = 7.0
    elif brand_match == "match" and material_match == "match":
        positive_rule = "BRAND_AND_MATERIAL_MATCH"
        positive_bonus = 7.0
    elif color_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
        positive_rule = "COLOR_AND_MULTIPLE_FEATURES_MATCH"
        positive_bonus = 5.0
    elif material_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
        positive_rule = "MATERIAL_AND_MULTIPLE_FEATURES_MATCH"
        positive_bonus = 5.0
    elif color_match == "match" and material_match == "match":
        positive_rule = "COLOR_AND_MATERIAL_MATCH"
        positive_bonus = 5.0
    elif location_match == "match" and feature_count >= MIN_FEATURES_STRONG_MATCH:
        positive_rule = "LOCATION_AND_FEATURE_MATCH"
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
    if "CORE_VISUAL_MISMATCH_VETO" in triggered_rules_list:
        status = "match_failure"
        evaluation_summary = "The reports have insufficient visual similarity to support a reliable match."
    elif final_score >= HIGH_THRESHOLD and positive_rule in (
        "ALL_MAJOR_ATTRIBUTES_AND_LOCATION_MATCH",
        "FOUR_FACTOR_MATCH",
        "BRAND_COLOR_FEATURE_MATCH",
        "COLOR_MATERIAL_FEATURE_MATCH",
        "COLOR_MATERIAL_BRAND_MATCH"
    ):
        status = "RECOMMENDED_MATCH"
        evaluation_summary = "Multiple independent attributes strongly support a potential match."
    elif final_score >= HIGH_THRESHOLD:
        status = "POTENTIAL_MATCH"
        evaluation_summary = "The reports show a high degree of similarity, but not all key attributes align."
    elif final_score >= REJECT_THRESHOLD:
        status = "POTENTIAL_MATCH"
        evaluation_summary = "The reports show a moderate degree of similarity, but some key attributes do not align."
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
    best_report = None
    best_evaluation = None
    for ai_result in ai_result_list:
        evaluation = evaluate_analysis(ai_result, lost_report_date)
        if evaluation["status"] in ("system_failure", "match_failure"):
            continue
        if best_evaluation is None:
            best_report = ai_result
            best_evaluation = evaluation
            continue
        if evaluation["final_composite_score"] > best_evaluation["final_composite_score"]:
            best_report = ai_result
            best_evaluation = evaluation
    if best_report is None:
        return None
    return {
        "report": best_report,
        "evaluation": best_evaluation
    }

#==========================================
# LOCAL VERIFICATION TEST BLOCK
#==========================================
# Make sure this block is at the very end of logic_manager.py
if __name__ == "__main__":
    # 1. Provide a dummy dataset to test with
    mock_ai_results = [
    {
        "report_type": "found",
        "category": "bottle",
        "date": "22-09-2026",
        "case_id": "CASE-20260922-6F1106.jpg",
        "image_filename": "CASE-20260922-6F1106.jpg",
        "primary_color": "white",
        "secondary_color": "black",
        "material": "stainless steel",
        "identifying_features": [
            "black flex cap with handle",
            "Hydro Flask logo on upper body",
            "Hydro Flask brand name printed at the bottom",
            "stainless steel rim"
        ],
        "brand": "Hydro Flask",
        "location_lost": "level 1 garden",
        "additional_notes": "Found at level 1 garden bench",
        "similarity_analysis": {
            "similarity_score": "100%",
            "color_match": {
                "is_match": "not match",
                "primary": "white",
                "secondary": "black"
            },
            "material_match": "not match",
            "feature_overlap_match": [
            ],
            "brand_match": "not match",
            "location_match": "match",
            "similarity_reasoning": "Identical match across all key attributes."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "18-09-2026",
        "case_id": "CASE-20260918-1A2B3C.jpg",
        "image_filename": "CASE-20260918-1A2B3C.jpg",
        "primary_color": "white",
        "secondary_color": "null",
        "material": "plastic",
        "identifying_features": [
            "plain clear shaker bottle",
            "blue measurement markings on side"
        ],
        "brand": "null",
        "location_lost": "level 1 garden",
        "additional_notes": "Found on 18th September, handed to security desk",
        "similarity_analysis": {
            "similarity_score": "95%",
            "color_match": {
                "is_match": "match",
                "primary": "white"
            },
            "material_match": "not match",
            "feature_overlap_match": [],
            "brand_match": "not match",
            "location_match": "match",
            "similarity_reasoning": "Matches color and location but differs in material, brand and features."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "22-09-2026",
        "case_id": "CASE-20260922-8A91B2.jpg",
        "image_filename": "CASE-20260922-8A91B2.jpg",
        "primary_color": "black",
        "secondary_color": "red",
        "material": "plastic",
        "identifying_features": [
            "sports push nozzle",
            "scratch on the lower base",
            "gym branding sticker"
        ],
        "brand": "nike",
        "location_lost": "level 1 garden",
        "additional_notes": "Left behind on a round outdoor table",
        "similarity_analysis": {
            "similarity_score": "95%",
            "color_match": "not match",
            "material_match": "not match",
            "feature_overlap_match": [],
            "brand_match": "not match",
            "location_match": "match",
            "similarity_reasoning": "Shares the same category and location but differs in visual attributes."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "20-09-2026",
        "case_id": "CASE-20260920-111111.jpg",
        "image_filename": "CASE-20260920-111111.jpg",
        "primary_color": "black",
        "secondary_color": "blue",
        "material": "plastic",
        "identifying_features": [
            "sports cap",
            "large logo"
        ],
        "brand": "Adidas",
        "location_lost": "level 2",
        "additional_notes": "Found near staircase",
        "similarity_analysis": {
            "similarity_score": "80%",
            "color_match": {
                "is_match": "match",
                "primary": "black"
            },
            "material_match": "not match",
            "feature_overlap_match": [
                "sports cap",
                "large logo"
            ],
            "brand_match": "not match",
            "location_match": "not match",
            "similarity_reasoning": "Color and features match."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "20-09-2026",
        "case_id": "CASE-20260920-222222.jpg",
        "image_filename": "CASE-20260920-222222.jpg",
        "primary_color": "silver",
        "secondary_color": "black",
        "material": "stainless steel",
        "identifying_features": [
            "metal cap",
            "large logo"
        ],
        "brand": "Hydro Flask",
        "location_lost": "level 2",
        "additional_notes": "Found beside classroom",
        "similarity_analysis": {
            "similarity_score": "70%",
            "color_match": "not match",
            "material_match": "match",
            "feature_overlap_match": [
                "metal cap",
                "large logo"
            ],
            "brand_match": "match",
            "location_match": "not match",
            "similarity_reasoning": "Material, brand and features match."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "20-09-2026",
        "case_id": "CASE-20260920-333333.jpg",
        "image_filename": "CASE-20260920-333333.jpg",
        "primary_color": "white",
        "secondary_color": "black",
        "material": "stainless steel",
        "identifying_features": [
            "black cap",
            "logo",
            "front marking"
        ],
        "brand": "Hydro Flask",
        "location_lost": "level 1",
        "additional_notes": "Found near library",
        "similarity_analysis": {
            "similarity_score": "75%",
            "color_match": {
                "is_match": "match",
                "primary": "white",
                "secondary": "black"
            },
            "material_match": "match",
            "feature_overlap_match": [
                "black cap",
                "logo",
                "front marking"
            ],
            "brand_match": "match",
            "location_match": "not match",
            "similarity_reasoning": "Color, material, brand and features all match."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "20-09-2026",
        "case_id": "CASE-20260920-444444.jpg",
        "image_filename": "CASE-20260920-444444.jpg",
        "primary_color": "white",
        "secondary_color": "black",
        "material": "stainless steel",
        "identifying_features": [
            "black cap",
            "logo",
            "front marking"
        ],
        "brand": "Hydro Flask",
        "location_lost": "level 1 garden",
        "additional_notes": "Found at garden bench",
        "similarity_analysis": {
            "similarity_score": "85%",
            "color_match": {
                "is_match": "match",
                "primary": "white",
                "secondary": "black"
            },
            "material_match": "match",
            "feature_overlap_match": [
                "black cap",
                "logo",
                "front marking"
            ],
            "brand_match": "match",
            "location_match": "match",
            "similarity_reasoning": "Strong match across all major attributes."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "20-09-2026",
        "case_id": "CASE-20260920-555555.jpg",
        "image_filename": "CASE-20260920-555555.jpg",
        "primary_color": "white",
        "secondary_color": "black",
        "material": "stainless steel",
        "identifying_features": [
            "black cap",
            "logo",
            "front marking",
            "silver rim"
        ],
        "brand": "Hydro Flask",
        "location_lost": "level 1 garden",
        "additional_notes": "Found near garden",
        "similarity_analysis": {
            "similarity_score": "80%",
            "color_match": {
                "is_match": "match",
                "primary": "white",
                "secondary": "black"
            },
            "material_match": "match",
            "feature_overlap_match": [
                "black cap",
                "logo",
                "front marking",
                "silver rim"
            ],
            "brand_match": "match",
            "location_match": "match",
            "similarity_reasoning": "Very strong match across all attributes."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "20-09-2026",
        "case_id": "CASE-20260920-666666.jpg",
        "image_filename": "CASE-20260920-666666.jpg",
        "primary_color": "red",
        "secondary_color": "black",
        "material": "plastic",
        "identifying_features": [],
        "brand": "null",
        "location_lost": "level 3",
        "additional_notes": "Found in hallway",
        "similarity_analysis": {
            "similarity_score": "75%",
            "color_match": "not match",
            "material_match": "not match",
            "feature_overlap_match": [],
            "brand_match": "not match",
            "location_match": "not match",
            "similarity_reasoning": "No major attributes match."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "20-09-2026",
        "case_id": "CASE-20260920-777777.jpg",
        "image_filename": "CASE-20260920-777777.jpg",
        "primary_color": "white",
        "secondary_color": "blue",
        "material": "plastic",
        "identifying_features": [
            "cap",
            "logo"
        ],
        "brand": "Nike",
        "location_lost": "level 1",
        "additional_notes": "Found near entrance",
        "similarity_analysis": {
            "similarity_score": "50%",
            "color_match": "match",
            "material_match": "not match",
            "feature_overlap_match": [
                "cap",
                "logo"
            ],
            "brand_match": "not match",
            "location_match": "match",
            "similarity_reasoning": "Only color and some features match."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "20-09-2026",
        "case_id": "CASE-20260920-888888.jpg",
        "image_filename": "CASE-20260920-888888.jpg",
        "primary_color": "white",
        "secondary_color": "black",
        "material": "stainless steel",
        "identifying_features": [
            "black cap",
            "logo"
        ],
        "brand": "Hydro Flask",
        "location_lost": "level 1",
        "additional_notes": "Found at level 1",
        "similarity_analysis": {
            "similarity_score": "90%",
            "color_match": {
                "is_match": "not match",
                "primary": "white",
                "secondary": "black"
            },
            "material_match": "match",
            "feature_overlap_match": [
                "black cap",
                "logo"
            ],
            "brand_match": "match",
            "location_match": "match",
            "similarity_reasoning": "Strong match across brand, color, material, location and features."
        }
    },

    {
        "report_type": "found",
        "category": "bottle",
        "date": "20-09-2026",
        "case_id": "CASE-20260920-999999.jpg",
        "image_filename": "CASE-20260920-999999.jpg",
        "primary_color": "white",
        "secondary_color": "black",
        "material": "stainless steel",
        "identifying_features": [
            "black cap",
            "logo",
            "silver rim"
        ],
        "brand": "Hydro Flask",
        "location_lost": "level 1 garden",
        "additional_notes": "Found on garden table",
        "similarity_analysis": {
            "similarity_score": "88%",
            "color_match": {
                "is_match": "match",
                "primary": "white",
                "secondary": "black"
            },
            "material_match": "match",
            "feature_overlap_match": [
                "black cap",
                "logo",
                "silver rim"
            ],
            "brand_match": "match",
            "location_match": "match",
            "similarity_reasoning": "Strong multi-attribute match."
        }
    }
]

    # 2. Run the logic
    user_lost_date = "15-09-2026"
    best_match_result = get_best_match(mock_ai_results, lost_report_date=user_lost_date)
    
    # 3. Print the output explicitly to the terminal
    print("\n--- BEST MATCH REPORT FOUND ---")
    print(json.dumps(best_match_result, indent=4))
