from pprint import pprint

from logic_manager import LogicManager
from logic_classes.threshold_config import ThresholdConfig


# 1. Create a configuration
try:
    threshold_config = ThresholdConfig(70, 90, 1, 2)
    # 2. Set the location preference
    threshold_config.consider_location = True

except ValueError as error:
    print(error)

# 3. Create LogicManager
logic_manager = LogicManager(
    threshold_config=threshold_config
)


# 4. Prepare sample AI output
# IMPORTANT:
# Copy the exact AI-result dictionaries from your existing
# passing Matcher tests. The structure must match what
# AnalysisValidator expects.

ai_result_list = [
    {
        "report_type": "found",
        "category": "bottle",
        "date": "27-09-2026",
        "case_id": "CASE-20260927-G77777.jpg",
        "image_filename": "CASE-20260927-G77777.jpg",
        "primary_color": "white",
        "secondary_color": "black",
        "material": "plastic",
        "identifying_features": [
            "flex cap",
            "logo"
        ],
        "brand": "Hydro Flask",
        "location_lost": "level 2 garden",
        "additional_notes": "Test multi-rule combination.",
        "similarity_analysis": {
            "similarity_score": "65%",
            "color_match": {
                "is_match": "match",
                "primary": "white",
                "secondary": "black"
            },
            "material_match": "not match",
            "feature_overlap_match": [
                "flex cap"
            ],
            "brand_match": "match",
            "location_match": "not match",
            "similarity_reasoning": "Color, brand and features match, but material and location differ."
        }
    },
    {
        "report_type": "found",
        "category": "bottle",
        "date": "27-09-2026",
        "case_id": "CASE-20260927-H88888.jpg",
        "image_filename": "CASE-20260927-H88888.jpg",
        "primary_color": "white",
        "secondary_color": "black",
        "material": "stainless steel",
        "identifying_features": [
            "flex cap",
            "logo"
        ],
        "brand": "Hydro Flask",
        "location_lost": "level 3 garden",
        "additional_notes": "Test multi-rule combination.",
        "similarity_analysis": {
            "similarity_score": "50%",
            "color_match": {
                "is_match": "match",
                "primary": "white",
                "secondary": "black"
            },
            "material_match": "match",
            "feature_overlap_match": [
                "flex cap",
                "logo"
            ],
            "brand_match": "match",
            "location_match": "not match",
            "similarity_reasoning": "Major item attributes match, but location differs."
        }
    },
    {
        "report_type": "found",
        "category": "bottle",
        "date": "27-09-2026",
        "case_id": "CASE-20260927-I99999.jpg",
        "image_filename": "CASE-20260927-I99999.jpg",
        "primary_color": "white",
        "secondary_color": "null",
        "material": "plastic",
        "identifying_features": [],
        "brand": "null",
        "location_lost": "level 1 garden",
        "additional_notes": "Test multi-rule combination.",
        "similarity_analysis": {
            "similarity_score": "50%",
            "color_match": {
                "is_match": "match",
                "primary": "white"
            },
            "material_match": "not match",
            "feature_overlap_match": [],
            "brand_match": "not match",
            "location_match": "match",
            "similarity_reasoning": "Only color and location provide support."
        }
    }
]


# 5. Supply the lost report date
lost_report_date = "25-09-2026"


# 6. Pass AI output into LogicManager
best_match = logic_manager.get_best_match(
    ai_result_list,
    lost_report_date
)


# 7. Display the result
print("\n========== LOGIC MANAGER TEST ==========")

print("\nBest Match:")
pprint(best_match)

print("\n========== TEST COMPLETED ==========")