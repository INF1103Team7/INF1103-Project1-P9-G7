# ai_manager file for AI API calling for feature extraction and semantic matching

# Import classes
from ai_classes.ai_service import AiService

# Class to manage AI services for feature extraction and semantic matching
class AiManager:
    def __init__(self):
        self._feature_extraction_service = AiService("Feature extraction")
        self._semantic_matching_service = AiService("Semantic AI matching")

    def extract_features(self, description, image_path: str = None):
        """_summary_
                Passes user text and optional image bytes to Gemini API with retry handling for feature extraction
            Args:
                description (str): User's description of the lost item
                image_path (str, optional): Path to the image file
            Returns:
                Extracted features as a JSON object or an error message.
        """
        return self._feature_extraction_service.extract_features(description, image_path)

    def ai_semantic_matching(self, input_lost_report, datalist: list):
        """_summary_
                Passes lost report and list of lost reports from database to Gemini API with retry handling for semantic matching
            Args:
                input_lost_report (str): User's lost report description
                datalist (list): List of lost reports from the database
            Returns:
                list of the top 3 most similar lost reports in order of similarity, with the most similar report first, or an error message.
        """
        return self._semantic_matching_service.ai_semantic_matching(input_lost_report, datalist)

# Testing 
desc = {
    "report_type": "lost",
    "category": "bottle",
    "description": "White bottle found at level 1 garden",
    "date": "22-09-2026",
    "case_id": "CASE-20260922-6F1106",
    "image_filename": "bottle.jpg"
}

extracted_desc = {
    "report_type": "lost",
    "category": "bottle",
    "date": "22-09-2026",
    "case_id": "CASE-20260922-6F1106",
    "image_filename": "bottle.jpg",
    "primary_color": "white",
    "secondary_color": "black",
    "material": "metal",
    "identifying_features": [
    "Black flex strap lid",
    "Hydro Flask logo printed on the front",
    "Stainless steel collar below lid"
    ],
    "brand": "Hydro Flask",
    "location_lost": "level 1 garden",
    "additional_notes": None
}

test_list = [
    {
        "report_type": "found",
        "category": "student card",
        "primary_color": None,
        "secondary_color": None,
        "material": None,
        "identifying_features": [
            "concession"
        ],
        "brand": None,
        "location_lost": None,
        "additional_notes": None,
        "date": "09-09-2026",
        "case_id": "CASE-20261008-174568",
        "status": "active"
    },
    {
        "report_type": "found",
        "category": "bottle",
        "primary_color": "white",
        "secondary_color": None,
        "material": None,
        "identifying_features": [
            "scratch"
        ],
        "brand": None,
        "location_lost": None,
        "additional_notes": None,
        "date": "09-10-2026",
        "case_id": "CASE-20261009-079A66",
        "status": "closed",
        "closed_date": "2026-10-09"
    },
    {
        "report_type": "found",
        "category": "bottle",
        "date": "09-09-2026",
        "primary_color": "white",
        "secondary_color": "black",
        "material": "stainless steel",
        "identifying_features": [
            "Hydro Flask logo in the center",
            "Black flex cap with carrying strap",
            "Brand name 'Hydro Flask' printed near the bottom",
            "Silver metallic band below the cap"
        ],
        "brand": "Hydro Flask",
        "location_lost": None,
        "additional_notes": None,
        "case_id": "CASE-20261009-BBAC7A",
        "image_filename": "CASE-20261009-BBAC7A.jpg",
        "status": "active"
    }
]

features = AiManager().extract_features(desc, desc["image_filename"])
# features = extract_features(desc, desc["image_filename"])
# match_result = AiManager().ai_semantic_matching(extracted_desc, test_list)
print(features)
# print(match_result)