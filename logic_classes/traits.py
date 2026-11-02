from .analysis_validator import AnalysisValidator

class Traits:
    """
    Responsible for extracting and classifying matching attributes from the AI analysis results.

    Uses AnalysisValidator to validate the reported timeline.
    """

    def __init__(self, validator=None):
        # Store the validator object.
        # A validator can be injected, or a new one is created by default.
        self.validator = validator or AnalysisValidator()

    def get_traits(self, ai_result, lost_report_date=None):
        # Access the similarity analysis returned by the AI.
        analysis = ai_result["similarity_analysis"]

        # Extract colour matching information.
        # Colour data may be a dictionary containing additional information or a simple string indicating whether the colours match.
        color_data = analysis.get("color_match", "not match")

        if isinstance(color_data, dict):
            color_match = color_data.get("is_match", "not match")
        else:
            color_match = color_data

        # Extract the remaining matching attributes.
        material_match = analysis.get("material_match", "not match")
        brand_match = analysis.get("brand_match", "not match")
        location_match = analysis.get("location_match", "not match")
        feature_overlaps = analysis.get("feature_overlap_match", [])

        # Use the validator to check whether the reported timeline is valid.
        time_match = self.validator.validate_timeline(
            ai_result,
            lost_report_date
        )

        # Return all extracted attributes in a dictionary for further evaluation.
        return {
            "color_match": color_match,
            "color_data": color_data,
            "material_match": material_match,
            "brand_match": brand_match,
            "location_match": location_match,
            "feature_overlaps": feature_overlaps,
            "time_match": time_match
        }

    def classify_traits(self, data):
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

        # Return the two lists separately for use by the matching rules.
        return matched, mismatched