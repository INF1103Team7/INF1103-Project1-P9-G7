import json
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
        Gemini API client if the GEMINI_API_KEY environment variable is set, otherwise returns None
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Gemini API Key not found. Please set the GEMINI_API_KEY environment variable.")
        return None
    return genai.Client(api_key=api_key)


def extract_features(description_text, image_bytes=None):
    """_summary_
        Passes user text and optional image bytes to Gemini API with retry handling for feature extraction
    Returns:
        JSON: Extracted features as a JSON object or an error message.
    """
    client = get_ai_client()
    if not client:
        return {"error": "API Key Missing"}

    prompt = f"""
    Extract structured lost/found item traits from this report:
    "{description_text}"
    
    Return strictly JSON:
    {
      "primary_color": "<color>",
      "secondary_color": "<color>",
      "material": "<material>",
      "identifying_features": ["<feature 1>, <feature 2>, ..."],
      "brand": "<brand>",
      "location_lost": "<location>",
      "additional_notes": "<notes>"
    }

    if any of the fields are not present in the report, return None for that field. Do not include any additional text or explanations in the response. Only return the JSON object as specified above.
    """

    contents = []
    if image_bytes:
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        )
    contents.append(prompt)

    # Configuration for the Gemini API request
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    # Retry loop for API calls, handling 503 errors
    delay = 5
    retries = 3
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config=config,
            )
            return json.loads(response.text.strip())

        except APIError as e:
            # Check for 503 server side error (High Demand / Unavailable) With exponential backoff retry
            if e.code == 503 and attempt < retries - 1:
                print(f"Model busy (503). Retrying in {delay}s... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)
                delay *= 2
                continue
            return {"error": str(e)}

        except Exception as e:
            return {"error": str(e)}

    return {"error": "Failed after max retries due to 503 UNAVAILABLE"}


desc = {
    "report_type": "lost",
    "case_id": "CASE-20260921-C180D4",
    "item_category": "wallet",
    "description": "Brown wallet near E2 at SIT got a black mark on the inside of the wallets",
    "date": "2026-5-1",
    "image_filename": "CASE-20260921-C180D4.png"
}

features = extract_features(desc)
print(features)
