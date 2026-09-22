import os
import time
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Surpress non critical logging messages from the Google GenAI library
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

# Load environment variables from .env file
load_dotenv()  

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

def extract_features(description, image_path=None):
    """_summary_
        Passes user text and optional image bytes to Gemini API with retry handling for feature extraction
    Returns:
        Extracted features as a JSON object or an error message.
    """
    print("[+] Initialising AI client object...")
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

    if any of the fields are not present in the report, return None for that field. Do not include any additional text or explanations in the response. Only return the JSON object as specified above.
    """
    print("[+] Checking for image filepath...")
    contents = []
    if image_path:
        print("[+] Image filepath found, attempting to add to prompt...")
        try:
            with open(f'./images/{image_path}', "rb") as f:
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

    print("[+] Prompt built, sending prompt to Gemini AI API")
    # Configuration for the Gemini API request
    config = types.GenerateContentConfig(
        response_mime_type = "application/json",
        temperature = 0.1,
        automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True),
        # Set request timeout 30 seconds
        http_options = types.HttpOptions(timeout = 60_000)
    )

    # Retry loop for API calls
    delay = 2
    retries = 3
    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config=config,
            )

            print("[+] Successful feature extraction")
            return response.text.strip()

        # Handle common API errors
        except APIError as e:
            # Handle error 429 resource exhausted (Rate limit exceeded)
            if e.code == 429:
                return f"[!] Error 429: Rate limit exceeded. {e.message}" 

            # Handle error 503 server side error (High Demand / Unavailable) With exponential backoff retry
            elif e.code == 503:
                if attempt < retries:
                    print(f"[!] Model busy (503). Retrying in {delay}s... (Attempt {attempt}/{retries})")
                if attempt == retries:
                    print(f"[!] Model busy (503). Max Retry reached (Attempt {attempt}/{retries})")
                    return f"[!] API Error {e.code}: {e.message}"
                attempt += 1
                time.sleep(delay)
                delay *= 2
                continue

        # Handle any other unexpected exceptions
        except Exception as e:
            return f"[!] Exception occured: {e}"
    return f"[!] Error: Feature extraction failed"

# Testing 
desc = {
    "report_type": "lost",
    "category": "bottle",
    "description": "White bottle found at level 1 garden",
    "date": "22-09-2026",
    "case_id": "CASE-20260922-6F1106",
    "image_filename": "CASE-20260922-6F110.jpg"
}

features = extract_features(desc, desc["image_filename"])
print(features)
