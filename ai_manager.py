import json
import os
from google import genai
from google.genai import types


def get_ai_client():
    """Initializes and returns the Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def extract_features_procedural(description_text, image_bytes=None):
    """Passes user text and optional image bytes to Gemini API."""
    client = get_ai_client()
    if not client:
        return {"error": "API Key Missing"}

    prompt = f"""
    Extract structured lost/found item traits from this report:
    "{description_text}"
    
    Return strictly JSON:
    {{
      "item_category": "<category>",
      "primary_color": "<color>",
      "material": "<material>",
      "identifying_features": ["<feature 1>"]
    }}
    """

    contents = []
    if image_bytes:
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        )
    contents.append(prompt)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.1
            ),
        )
        return json.loads(response.text.strip())
    except Exception as e:
        return {"error": str(e)}