import time
from typing import Optional, Any
from google.genai.errors import APIError
from ai_classes.ai_service_interface import AIServiceInterface
from ai_classes.ai_api import AiAPI
from ai_classes.ai_helper import AiHelper
from ai_classes.ai_configuration import AiConfiguration

class AiService(AIServiceInterface):
    # Class initialization with operation type
    def __init__(self, operation_type: str):
        self._client = AiAPI()._get_ai_client()
        self._operation_type = operation_type

    # Execute API call with retry logic
    def _execute_with_retry(self, contents: Any):
        """_summary_
            Method to execute the AI API call with retry logic for handling rate limits and service unavailability.
        Args:
            contents (Any): Prompt contents to be sent to the AI API, can include text and/or image bytes.

        Returns:
            str: The response from the AI API, stripped of leading and trailing whitespace. or None if an error occurs.
        """
        # Retry loop for API calls in the case of 429 Resource exhausted errors
        ai_configurations = AiConfiguration()
        for model_index, active_model in enumerate(ai_configurations.models):
            print(f"[+] Active model in use {active_model}")
            # Retry loop for API calls in the case of 503 service unavailable errors
            delay = 5
            retries = 3
            for attempt in range(1, retries + 1):
                try:
                    response = self._client.models.generate_content(
                        model=active_model,
                        contents=contents,
                        config=ai_configurations.config,
                    )
    
                    print(f"[+] Successful {self._operation_type}")
                    return response.text.strip()
    
                # Handle common API errors
                except APIError as e:
                    # Handle error 429 resource exhausted (Rate limit exceeded) and retry with backup models
                    if e.code == 429:
                        print(f"[!] API Error 429: Rate limit hit on {active_model}")
                        if model_index < len(ai_configurations.models) - 1:
                            next_model = ai_configurations.models[model_index + 1]
                            print(f"[+] Trying next model: {next_model}")
                        else:
                            print(f"[!] API Error 429: All models rate limit exceeded. {e.message}")
                            return None
                        break 
    
                    # Handle error 503 server side error (High Demand / Unavailable) With exponential backoff retry
                    elif e.code == 503:
                        if attempt < retries:
                            print(f"[!] API Error 503: Model busy. Retrying in {delay}s... (Attempt {attempt}/{retries})")
                        if attempt == retries:
                            print(f"[!] API Error 503: Model busy. Max Retry reached (Attempt {attempt}/{retries})")
                            print(f"[!] API Error {e.code}: {e.message}")
                        
                        attempt += 1
                        time.sleep(delay)
                        delay *= 2
                        continue
                    else:
                        print(f"[!] API Error {e.code}: {e.message}")
                        return None
    
                # Handle any other unexpected exceptions
                except Exception as e:
                    print(f"[!] Exception occured: {e}")
                    return None
        print(f"[!] Error: {self._operation_type} failed")
        return None

    # Feature extraction service method
    def extract_features(self, description, image_path: Optional[str] = None):
        """_summary_
                Passes user text and optional image bytes to Gemini API with retry handling for feature extraction
            Args:
                description (str): User's description of the lost item
                image_path (str, optional): Path to the image file
            Returns:
                Extracted features as a JSON object or an error message.
        """
        print("[+] Initialising AI client object for feature extraction...")
        if not self._client:
            print(f"[!] Error: Gemini API Key missing")
            return None
        print("[+] AI client object initialised successfully!")
        print("[+] Building AI Prompt...")
    
        prompt = f"""
        Extract structured lost/found item traits from this report:
        "{description}"
        
        Return strictly JSON ensuring that it is double quoted and replace description with the following fields while keeping all other fields untouched from the original report:
        {{
            "primary_color": "<color>",
            "secondary_color": "<color>",
            "material": "<material>",
            "identifying_features": ["<feature 1>, <feature 2>, ..."],
            "brand": "<brand>",
            "location_lost": "<location>",
            "additional_notes": "<notes>"
        }}
    
        If any of the fields are not present in the report, return None for that field. Do not include any additional text or explanations in the response. 
        Only return the JSON object as specified above.
        """
        print("[+] Checking for image filepath...")
        contents = []
        if image_path:
            print("[+] Image filepath found, attempting to add to prompt...")
            contents.append(AiHelper()._load_image_part(image_path))
        
        contents.append(prompt)
        print("[+] Feature extraction prompt built, sending prompt to Gemini AI API")
        return self._execute_with_retry(contents)

    # Semantic matching service method
    def ai_semantic_matching(self, input_lost_report, datalist: list):
        """_summary_
                Passes lost report and list of lost reports from database to Gemini API with retry handling for semantic matching
            Args:
                input_lost_report (str): User's lost report description
                datalist (list): List of lost reports from the database
            Returns:
                list of the top 3 most similar lost reports in order of similarity, with the most similar report first, or an error message.
        """
        print("[+] Initialising AI client object for semantic matching...")
        client = AiAPI()._get_ai_client()
        if not client:
            print(f"[!] Error: Gemini API Key missing")
            return None
        print("[+] AI client object initialised successfully!")
        print("[+] Building Semantic AI Matching Prompt...")
    
        prompt = f"""
        From this list of objects containing found reports "{datalist}", rank the top 3 most similar objects compared to this report:
        "{input_lost_report}"
        
        Return a list conataining the top 3 most similar objects in order of similarity, with the most similar object first. 
        Each object should be represented as a JSON object containing the original fields with these additional fields stored as a nested object named similarity_analysis at the end of each object:
        {{
            "similarity_score": "<score between 0% and 100%>",
            "color_match": "<Nested object, specifications at the end of prompt>",
            "material_match": "<match / not match>",
            "feature_overlap_match": "<list (list of strings) of overlapping features>",
            "brand_match": "<match / not match>",
            "location_match": "<match / not match>",
            "similarity_reasoning": "<overall reasoning for similarity score based on the above fields>"
        }}
    
        Specifications to extract and evaluate the color alignment between the two items for the "color_match" field above according to these strict conditional schema rules:
    
        1. IF NO COLORS MATCH:
        Return a simple string value:
        "color_match": "not match"
    
        2. IF PRIMARY COLOR MATCHES:
        Nested object with "is_match" and "primary" keys:
        "color_match": {{
            "is_match": "match",
            "primary": "<matched_primary_color>"
        }}
    
        3. IF SECONDARY COLOR MATCHES:
        Nested object with "is_match" and "secondary" keys:
        "color_match": {{
            "is_match": "match",
            "secondary": "<matched_secondary_color>"
        }}
    
        4. IF BOTH PRIMARY AND SECONDARY COLORS MATCH:
        Nested object with "is_match", "primary", and "secondary" keys:
        "color_match": {{
            "is_match": "match",
            "primary": "<matched_primary_color>",
            "secondary": "<matched_secondary_color>"
        }}
        """
    
        print("[+] Semantic AI Matching prompt built, sending prompt to Gemini AI API")
        return self._execute_with_retry(prompt)
