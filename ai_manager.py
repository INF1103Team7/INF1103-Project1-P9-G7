import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Surpress non critical logging messages from the Google GenAI library
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

# Gemini AI models to use
AI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]
# Configuration for the Gemini API request
AI_CONFIG = types.GenerateContentConfig (
    response_mime_type = "application/json",
    temperature = 0.1,
    automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True),
    # Set request timeout 30 seconds
    http_options = types.HttpOptions(timeout = 60_000)
)

# Load environment variables from .env file
load_dotenv()  

# Functions
def get_ai_client():
    """_summary_
        Sets up the Gemini AI API client using the GEMINI API Key from the .env file
    Returns:
        Google genai.Client Object: Gemini API client if the GEMINI_API_KEY environment variable is set, otherwise returns None
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Gemini API Key not found. Please set the GEMINI_API_KEY environment variable.")
        return None
    return genai.Client(api_key=api_key)

def get_mime_type(filename: str) -> str:
    """_summary_
        Helper function to get mimetype based on the image filename extension
    Args:
        filename (str): Image filename

    Returns:
        str: Mimetype to be passed in AI API request
    """
    extension = filename.lower().rsplit(".", 1)[-1]
    if extension in ["jpg", "jpeg"]:
        return "image/jpeg"
    elif extension == "png":
        return "image/png"
    
    # Universal fallback in case of any unexpected issues
    return "application/octet-stream"

def extract_features(description, image_path=None):
    """_summary_
            Passes user text and optional image bytes to Gemini API with retry handling for feature extraction
        Args:
            description (str): User's description of the lost item
            image_path (str, optional): Path to the image file
        Returns:
            Extracted features as a JSON object or an error message.
    """
    print("[+] Initialising AI client object for feature extraction...")
    client = get_ai_client()
    if not client:
        return f"[!] Error: Gemini API Key missing"
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
        try:
            with open(Path(__file__).parent / f"images/{image_path}", "rb") as f:
                image_bytes = f.read()

            contents.append(
                types.Part.from_bytes(data = image_bytes, mime_type = get_mime_type(image_path))
            )

            print("[+] Image successfully added to prompt!")
        # Handle File not found error
        except FileNotFoundError:
            print(f"[!] File {image_path} not found, continuing extraction without image")

        # Handle any other unexpected exceptions
        except Exception as e:
            print(f"[!] Exception occured: {e}")

    contents.append(prompt)

    print("[+] Feature extraction prompt built, sending prompt to Gemini AI API")
    # Retry loop for API calls in the case of 429 Resource exhausted errors
    for model_index, active_model in enumerate(AI_MODELS):
        print(f"[+] Active model in use {active_model}")
        # Retry loop for API calls in the case of 503 service unavailable errors
        delay = 5
        retries = 3
        for attempt in range(1, retries + 1):
            try:
                response = client.models.generate_content(
                    model=active_model,
                    contents=contents,
                    config=AI_CONFIG,
                )

                print("[+] Successful feature extraction")
                return response.text.strip()

            # Handle common API errors
            except APIError as e:
                # Handle error 429 resource exhausted (Rate limit exceeded) and retry with backup models
                if e.code == 429:
                    print(f"[!] API Error 429: Rate limit hit on {active_model}")
                    if model_index < len(AI_MODELS) - 1:
                        next_model = AI_MODELS[model_index + 1]
                        print(f"[+] Trying next model: {next_model}")
                    else:
                        return f"[!] API Error 429: All models rate limit exceeded. {e.message}"
                    break 

                # Handle error 503 server side error (High Demand / Unavailable) With exponential backoff retry
                elif e.code == 503:
                    if attempt < retries:
                        print(f"[!] API Error 503: Model busy. Retrying in {delay}s... (Attempt {attempt}/{retries})")
                    if attempt == retries:
                        print(f"[!] API Error 503: Model busy. Max Retry reached (Attempt {attempt}/{retries})")
                        return f"[!] API Error {e.code}: {e.message}"
                    attempt += 1
                    time.sleep(delay)
                    delay *= 2
                    continue

            # Handle any other unexpected exceptions
            except Exception as e:
                return f"[!] Exception occured: {e}"
    return f"[!] Error: Feature extraction failed"

def ai_semantic_matching(input_lost_report, datalist: list):
    """_summary_
            Passes lost report and list of lost reports from database to Gemini API with retry handling for semantic matching
        Args:
            input_lost_report (str): User's lost report description
            datalist (list): List of lost reports from the database
        Returns:
            list of the top 3 most similar lost reports in order of similarity, with the most similar report first, or an error message.
    """
    print("[+] Initialising AI client object for feature extraction...")
    client = get_ai_client()
    if not client:
        return f"[!] Error: Gemini API Key missing"
    print("[+] AI client object initialised successfully!")
    print("[+] Building Semantic AI Matching Prompt...")

    prompt = f"""
    From this list of objects containing found reports "{datalist}", rank the top 3 most similar objects compared to this report:
    "{input_lost_report}"
    
    Return a list conataining the top 3 most similar objects in order of similarity, with the most similar object first. 
    Each object should be represented as a JSON object containing the original fields with these additional fields stored as a nested object named similarity_analysis at the end of each object:
    {{
        "similarity_score": "<score between 0% and 100%>",
        "color_match": "<match / not match, which colour was matched, reasoning for color match>",
        "material_match": "<match / not match>",
        "feature_overlap_match": "<list (list of strings) of overlapping features>",
        "brand_match": "<match / not match>",
        "location_match": "<match / not match>",
        "similarity_reasoning": "<overall reasoning for similarity score based on the above fields>"
    }}
    """

    print("[+] Semantic AI Matching prompt built, sending prompt to Gemini AI API")
    # Retry loop for API calls in the case of 429 Resource exhausted errors
    for model_index, active_model in enumerate(AI_MODELS):
        print(f"[+] Active model in use {active_model}")
        # Retry loop for API calls in the case of 503 service unavailable errors
        delay = 5
        retries = 3
        for attempt in range(1, retries + 1):
            try:
                response = client.models.generate_content(
                    model=active_model,
                    contents=prompt,
                    config=AI_CONFIG,
                )

                print("[+] Successful Semantic AI matching extraction")
                return response.text.strip()

            # Handle common API errors
            except APIError as e:
                # Handle error 429 resource exhausted (Rate limit exceeded) and retry with backup models
                if e.code == 429:
                    print(f"[!] API Error 429: Rate limit hit on {active_model}")
                    if model_index < len(AI_MODELS) - 1:
                        next_model = AI_MODELS[model_index + 1]
                        print(f"[+] Trying next model: {next_model}")
                    else:
                        return f"[!] API Error 429: All models rate limit exceeded. {e.message}"
                    break 

                # Handle error 503 server side error (High Demand / Unavailable) With exponential backoff retry
                elif e.code == 503:
                    if attempt < retries:
                        print(f"[!] API Error 503: Model busy. Retrying in {delay}s... (Attempt {attempt}/{retries})")
                    if attempt == retries:
                        print(f"[!] API Error 503: Model busy. Max Retry reached (Attempt {attempt}/{retries})")
                        return f"[!] API Error {e.code}: {e.message}"
                    attempt += 1
                    time.sleep(delay)
                    delay *= 2
                    continue

            # Handle any other unexpected exceptions
            except Exception as e:
                return f"[!] Exception occured: {e}"
    return f"[!] Error: Semantic AI matching failed"

# Testing 
found_report = {
    "report_type": "found",
    "category": "bottle",
    "description": "White bottle found at level 1 garden",
    "date": "22-09-2026",
    "case_id": "CASE-20260922-6F1106.jpg",
    "image_filename": "CASE-20260922-6F1106.jpg"
}

lost_report_ai_extracted = {
  "report_type": "lost",
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
  "additional_notes": "Found at level 1 garden"
}

test_found_database = [
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
    "additional_notes": "Found at level 1 garden bench"
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
    "additional_notes": "Left behind on a round outdoor table"
  },
  {
    "report_type": "found",
    "category": "electronics",
    "date": "21-09-2026",
    "case_id": "CASE-20260921-3C4D5E.jpg",
    "image_filename": "CASE-20260921-3C4D5E.jpg",
    "primary_color": "space grey",
    "secondary_color": "black",
    "material": "aluminum",
    "identifying_features": [
      "laptop inside a black felt sleeve",
      "developer sticker on top right corner",
      "small dent on hinge"
    ],
    "brand": "apple",
    "location_lost": "library level 2",
    "additional_notes": "Handed over to library counter staff"
  },
  {
    "report_type": "found",
    "category": "wallet",
    "date": "23-09-2026",
    "case_id": "CASE-20260923-7F8E9D.jpg",
    "image_filename": "CASE-20260923-7F8E9D.jpg",
    "primary_color": "brown",
    "secondary_color": "null",
    "material": "leather",
    "identifying_features": [
      "foldable bi-fold style",
      "contains student id card",
      "silver zipper coin pocket"
    ],
    "brand": "fossil",
    "location_lost": "canteen 2",
    "additional_notes": "Found under a dining chair during lunch hour"
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
    "additional_notes": "Found on 18th September, handed to security desk"
  }
]

# features = extract_features(found_report, found_report["image_filename"])
# print(features)
match_list = ai_semantic_matching(lost_report_ai_extracted, test_found_database)
print(match_list)
