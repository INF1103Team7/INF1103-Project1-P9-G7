import json

REJECT_THRESHOLD = 50


# ============================================================
# DATA / VALIDATION
# ============================================================

def get_reports_by_category(category):
    report_list = []

    try:
        with open("reports.json", "r") as f:
            reports = json.load(f)

        for report in reports:
            if report.get("category") == category:
                report_list.append(report)

    except FileNotFoundError:
        print("The file reports.json is not found!")

    except json.JSONDecodeError:
        print("Error: The file reports.json is corrupted!")

    return report_list


def parse_score_to_float(score):
    if not isinstance(score, str):
        return None

    if not score.endswith("%"):
        return None

    try:
        score = float(score[:-1])

        if not 0 <= score <= 100:
            return None

        return score

    except ValueError:
        return None


def validate_analysis(ai_result):
    if not isinstance(ai_result, dict):
        return "system_failure", None

    similarity_analysis = ai_result.get("similarity_analysis")

    if not isinstance(similarity_analysis, dict):
        return "system_failure", None

    similarity_score = similarity_analysis.get("similarity_score")

    score = parse_score_to_float(similarity_score)

    if score is None:
        return "system_failure", None

    return "valid", score


# ============================================================
# EXTRACT AI DATA
# ============================================================

def extract_analysis_data(ai_result):
    analysis = ai_result["similarity_analysis"]

    # ----------------------------
    # Color
    # ----------------------------

    color_match_data = analysis.get(
        "color_match",
        "not match"
    )

    if isinstance(color_match_data, dict):
        color_match = color_match_data.get(
            "is_match",
            "not match"
        )
    else:
        color_match = color_match_data

    # ----------------------------
    # Material
    # ----------------------------

    material_match = analysis.get(
        "material_match",
        "not match"
    )

    # ----------------------------
    # Brand
    # ----------------------------

    brand_match = analysis.get(
        "brand_match",
        "not match"
    )

    # ----------------------------
    # Location
    # ----------------------------

    location_match = analysis.get(
        "location_match",
        "not match"
    )

    # ----------------------------
    # Feature overlaps
    # ----------------------------

    feature_overlaps = analysis.get(
        "feature_overlap_match",
        []
    )

    if not isinstance(feature_overlaps, list):
        feature_overlaps = []

    return {
        "color_match": color_match,
        "color_match_data": color_match_data,
        "material_match": material_match,
        "brand_match": brand_match,
        "location_match": location_match,
        "feature_overlaps": feature_overlaps,
    }

# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================
def evaluate_analysis(ai_result):

    # ==========================================
    # 1. VALIDATE AI RESULT
    # ==========================================

    validation, similarity_score = validate_analysis(ai_result)

    if validation == "system_failure":
        return {
            "status": "system_failure",
            "final_composite_score": None,
            "triggered_rules_list": [],
            "evaluation_summary": "Invalid AI output."
        }

    # ==========================================
    # 2. EXTRACT AI DATA
    # ==========================================

    data = extract_analysis_data(ai_result)

    color_match = data["color_match"]
    color_match_data = data["color_match_data"]
    material_match = data["material_match"]
    brand_match = data["brand_match"]
    location_match = data["location_match"]
    feature_overlaps = data["feature_overlaps"]

    final_score = similarity_score

    triggered_rules_list = []

    # ==========================================
    # 3. BUSINESS RULES
    # ==========================================

    # Rule 1: Visual & Material Not Match
    # Hard Veto
    if (
        color_match == "not match"
        and material_match == "not match"
        and len(feature_overlaps) == 0
    ):

        triggered_rules_list.append(
            "VISUAL_MATERIAL_NOT_MATCHED_VETO"
        )

        return {
            "status": "match_failure",
            "final_composite_score": min(
                final_score,
                30.0
            ),
            "triggered_rules_list":
                triggered_rules_list,
            "evaluation_summary":
                "Visual, material and feature "
                "information did not support a match."
        }

    # ------------------------------------------
    # Rule 2: Partial Visual Match Penalty
    # ------------------------------------------

    if (
        color_match == "match"
        and brand_match == "not match"
        and material_match == "not match"
    ):

        final_score = max(
            0.0,
            final_score - 15.0
        )

        triggered_rules_list.append(
            "GENERIC_COLOR_ONLY_PENALTY"
        )

    # ------------------------------------------
    # Rule 3: Full Color Match
    # ------------------------------------------

    if (
        isinstance(color_match_data, dict)
        and "secondary" in color_match_data
        and color_match == "match"
        and material_match == "match"
    ):

        triggered_rules_list.append(
            "FULL_COLOR_MATCH"
        )

    # ------------------------------------------
    # Rule 4: Color + Features
    # ------------------------------------------

    if (
        color_match == "match"
        and len(feature_overlaps) >= 2
    ):

        triggered_rules_list.append(
            "COLOR_FEATURE_MATCH"
        )

    # ------------------------------------------
    # Rule 5: Material + Features
    # ------------------------------------------

    if (
        material_match == "match"
        and len(feature_overlaps) >= 2
    ):

        triggered_rules_list.append(
            "MATERIAL_FEATURE_MATCH"
        )

    # ------------------------------------------
    # Rule 6: Brand Match
    # ------------------------------------------

    if brand_match == "match":

        triggered_rules_list.append(
            "BRAND_MATCH"
        )

    # ------------------------------------------
    # Rule 7: Brand + Color
    # ------------------------------------------

    if (
        brand_match == "match"
        and color_match == "match"
    ):

        triggered_rules_list.append(
            "BRAND_COLOR_MATCH"
        )

    # ------------------------------------------
    # Rule 8: Brand + Features
    # ------------------------------------------

    if (
        brand_match == "match"
        and len(feature_overlaps) >= 2
    ):

        triggered_rules_list.append(
            "BRAND_FEATURE_MATCH"
        )

    # ------------------------------------------
    # Rule 9: Location Match
    # ------------------------------------------

    if location_match == "match":

        triggered_rules_list.append(
            "LOCATION_MATCH"
        )

    # ------------------------------------------
    # Rule 10: Location + Features
    # ------------------------------------------

    if (
        location_match == "match"
        and len(feature_overlaps) >= 2
    ):

        triggered_rules_list.append(
            "LOCATION_FEATURE_MATCH"
        )

    # ------------------------------------------
    # Rule 11: Location + Brand
    # ------------------------------------------

    if (
        location_match == "match"
        and brand_match == "match"
    ):

        triggered_rules_list.append(
            "LOCATION_BRAND_MATCH"
        )

    # ------------------------------------------
    # Rule 12: High Similarity
    # ------------------------------------------

    if final_score >= 80:

        triggered_rules_list.append(
            "HIGH_SIMILARITY"
        )

    # ------------------------------------------
    # Rule 13: High Similarity + Brand
    # ------------------------------------------

    if (
        final_score >= 80
        and brand_match == "match"
    ):

        triggered_rules_list.append(
            "HIGH_SIMILARITY_BRAND"
        )

    # ------------------------------------------
    # Rule 14: High Similarity + Features
    # ------------------------------------------

    if (
        final_score >= 80
        and len(feature_overlaps) >= 2
    ):

        triggered_rules_list.append(
            "HIGH_SIMILARITY_FEATURES"
        )

    # ------------------------------------------
    # Rule 15: High Confidence
    # ------------------------------------------

    if (
        final_score >= 80
        and brand_match == "match"
        and color_match == "match"
        and material_match == "match"
        and len(feature_overlaps) >= 2
    ):

        triggered_rules_list.append(
            "HIGH_CONFIDENCE_MATCH"
        )

    # ------------------------------------------
    # Rule 16: Everything Matches
    # ------------------------------------------

    if (
        color_match == "match"
        and material_match == "match"
        and brand_match == "match"
        and location_match == "match"
        and len(feature_overlaps) >= 2
    ):

        triggered_rules_list.append(
            "ALL_ATTRIBUTES_MATCH"
        )

    # ==========================================
    # 4. FINAL DECISION
    # ==========================================

    if "ALL_ATTRIBUTES_MATCH" in triggered_rules_list:

        status = "RECOMMENDED_MATCH"

        summary = (
            "All major identifying attributes matched."
        )

    elif "HIGH_CONFIDENCE_MATCH" in triggered_rules_list:

        status = "RECOMMENDED_MATCH"

        summary = (
            "High similarity combined with matching "
            "brand, color, material and multiple "
            "feature overlaps."
        )

    elif (
        len(triggered_rules_list) >= 3
        and final_score >= 70
    ):

        status = "POTENTIAL_MATCH"

        summary = (
            "Multiple business rules were triggered "
            "and support a potential match."
        )

    elif final_score >= 50:

        status = "POTENTIAL_MATCH"

        summary = (
            "The report meets the minimum similarity "
            "threshold for consideration."
        )

    else:

        status = "match_failure"

        summary = (
            "The report did not provide sufficient "
            "evidence for a potential match."
        )

    # ==========================================
    # 5. RETURN BUSINESS LOGIC RESULT
    # ==========================================

    return {
        "status": status,
        "final_composite_score": final_score,
        "triggered_rules_list": triggered_rules_list,
        "evaluation_summary": summary
    }
def get_final_report(ai_result_list):

    evaluated_reports = []

    for ai_result in ai_result_list:

        result = evaluate_analysis(ai_result)

        if result["status"] == "system_failure":
            continue

        if result["status"] == "match_failure":
            continue

        evaluated_reports.append({
            "report": ai_result,
            "logic_result": result
        })

    if not evaluated_reports:
        return {
            "status": "match_failure",
            "message": "No suitable matches were found.",
            "matches": []
        }

    evaluated_reports.sort(
        key=lambda x: x["logic_result"]["final_composite_score"],
        reverse=True
    )

    final_matches = []

    for item in evaluated_reports:

        report = item["report"]
        logic_result = item["logic_result"]

        final_matches.append({
            "case_id": report.get("case_id"),
            "category": report.get("category"),
            "similarity_score":
                logic_result["final_composite_score"],
            "status": logic_result["status"],
            "triggered_rules":
                logic_result["triggered_rules_list"],
            "evaluation":
                logic_result["evaluation_summary"]
        })

    return {
        "status": "success",
        "matches": final_matches
    }