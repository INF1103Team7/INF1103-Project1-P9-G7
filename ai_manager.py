# ai_manager file for AI API calling for feature extraction and semantic matching

# Import classes
from ai_classes.ai_service import AiService


# Class to manage AI services for feature extraction and semantic matching
class AiManager:
    # Class initialization method to set up AI services for feature extraction and semantic matching
    def __init__(self):
        self._feature_extraction_service = AiService("Feature extraction")
        self._semantic_matching_service = AiService("Semantic AI matching")

    def extract_features(self, description: str, image_path: str | None = None):
        """_summary_
                Passes user text and optional image bytes to Gemini API with retry handling for feature extraction
            Args:
                description (str): User's description of the lost item
                image_path (str, optional): Path to the image file
            Returns:
                Extracted features as a JSON object or an error message.
        """
        return self._feature_extraction_service.extract_features(description, image_path)

    def ai_semantic_matching(self, input_lost_report: str, datalist: list):
        """_summary_
                Passes lost report and list of lost reports from database to Gemini API with retry handling for semantic matching
            Args:
                input_lost_report (str): User's lost report description
                datalist (list): List of lost reports from the database
            Returns:
                list of the top 3 most similar lost reports in order of similarity, with the most similar report first, or an error message.
        """
        return self._semantic_matching_service.ai_semantic_matching(input_lost_report, datalist)

# Import control
__all__ = ["AiManager"]
