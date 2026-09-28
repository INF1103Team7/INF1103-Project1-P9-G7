#found > io > ai > logic - pull from db via keys to send back ai; for loop to store in array > ai count score > logic > user

import json
from typing import Any, Dict, Union

# Threshold for AI similarity score below which a match is considered a failure
REJECT_THRESHOLD = 80

# 1 Get all records by category from database.py that match the specified category from the lost report description.
def get_reports_by_category(category):
    report_list = []
    try:
        with open("reports.json", "r") as f:
            reports = json.load(f)
            for report in reports:
                category_to_get = report.get("category")
                if category == category_to_get:
                    report_list.append(report)
    except FileNotFoundError:
        print("The file reports.json is not found!")
    except json.JSONDecodeError:
        print("Error: The file reports.json is corrupted!!")
    return report_list

# 2 Validate the AI result against business rules and record statuses.
def parse_score_to_float(score):

    if not isinstance(score, str):
        return None

    if not score.endswith("%"):
        return None

    try:
        ai_score = float(score[:-1])

        if not 0 <= ai_score <= 100:
            return None

    except ValueError:
        return None

    return ai_score


def validate_analysis(ai_result):

    # Check that the AI result is a dictionary
    if not isinstance(ai_result, dict):
        return "system_failure"

    # Get the similarity_analysis dictionary
    similarity_analysis = ai_result.get("similarity_analysis")

    if not isinstance(similarity_analysis, dict):
        return "system_failure"

    # Get similarity score from similarity_analysis
    similarity_score = similarity_analysis.get("similarity_score")

    # Convert "100%" into 100.0
    score_float = parse_score_to_float(similarity_score)

    if score_float is None:
        return "system_failure"

    return "valid"

def get_logic_analysis(report):
    analysis = report.get("similarity_analysis")
    if not isinstance(analysis, dict):
        return {
            "status": "system_failure",
            "reason": "Missing similarity analysis."
        }
    score = parse_score_to_float(
        analysis.get("similarity_score")
    )

    if score is None:
        return {
            "status": "system_failure",
            "reason": "Invalid similarity score"
        }

    # AI match information
    color_match = analysis.get("color_match")
    material_match = analysis.get("material_match")
    brand_match = analysis.get("brand_match")
    location_match = analysis.get("location_match")
    features = analysis.get("feature_overlap_match")
        
    color = (
        isinstance(color_match, str)
        and color_match.lower().strip() == "match"
    )

    material = (
        isinstance(material_match, str)
        and material_match.lower().strip() == "match"
    )

    brand = (
        isinstance(brand_match, str)
        and brand_match.lower().strip() == "match"
    )

    location = (
        isinstance(location_match, str)
        and location_match.lower().strip() == "match"
    )

    feature_match = (
        isinstance(features, list)
        and len(features) > 0
    )

    strong_rule = (
        brand
        and material
        and feature_match
    )

    alternate_strong_rule = (
        brand
        and color
        and feature_match
    )

    moderate_rule = (
        color
        and location
        and feature_match
    )

    alternate_moderate_rule = (
        material
        and brand
        and location
    )

    weak_rule = (
        color
        and location
        and not material
        and not brand
        and not feature_match
    )

    contradiction_rule = (
        not material
        and not brand
        and not feature_match
    )

    false_positive = (
        score >= REJECT_THRESHOLD
        and contradiction_rule
    )

    false_negative = (
        score < REJECT_THRESHOLD
        and (
            strong_rule
            or alternate_strong_rule
        )
    )

    if false_positive:

        decision = "reject"
        reason = (
            "AI score is high but important identifying attributes do not match."
        )

    elif false_negative:

        decision = "review"
        reason = (
            "AI score is below the threshold but several strong identifying attributes match."
        )

    elif strong_rule or alternate_strong_rule:

        decision = "strong_match"
        reason = (
            "Multiple strong identifying attributes match."
        )

    elif moderate_rule or alternate_moderate_rule:

        decision = "possible_match"
        reason = (
            "Several relevant attributes match."
        )

    elif weak_rule:

        decision = "reject"
        reason = (
            "Only weak attributes such as color and location match."
        )

    else:

        decision = "reject"
        reason = (
            "Insufficient matching attributes."
        )

    return {
        "status": "valid",
        "decision": decision,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "ai_score": score,
        "rules": {
            "strong_rule": strong_rule,
            "alternate_strong_rule": alternate_strong_rule,
            "moderate_rule": moderate_rule,
            "alternate_moderate_rule": alternate_moderate_rule,
            "weak_rule": weak_rule,
            "contradiction_rule": contradiction_rule
        },
        "reason": reason
    }

def get_top_matches(ai_result_list, limit=5):

    valid_reports_list = []

    for report in ai_result_list:

        validation = validate_analysis(report)

        if validation == "system_failure":
            continue

        rule_result = get_logic_analysis(report)

        if rule_result["status"] == "system_failure":
            continue

        # Store logic result inside the report
        report["logic_analysis"] = rule_result

        if rule_result["decision"] in [
            "strong_match",
            "possible_match",
            "review"
        ]:

            valid_reports_list.append(report)

    # Sort by AI score
    valid_reports_list.sort(
        key=lambda report:
        report["logic_analysis"]["ai_score"],
        reverse=True
    )

    return valid_reports_list[:limit]