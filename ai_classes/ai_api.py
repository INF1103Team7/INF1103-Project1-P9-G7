import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


class AiAPI:
    def __init__(self):
        load_dotenv(Path(__file__).parent.parent / ".env")  # Load environment variables from .env file
        self._api_key = os.environ.get("GEMINI_API_KEY")
    
    def _get_ai_client(self) -> genai.Client:
        """_summary_
            Sets up the Gemini AI API client using the GEMINI API Key from the .env file
        Returns:
            Google genai.Client Object: Gemini API client if the GEMINI_API_KEY environment variable is set, otherwise returns None
        """

        if not self._api_key:
            print("Gemini API Key not found. Please set the GEMINI_API_KEY environment variable.")
            return None
        return genai.Client(api_key=self._api_key)

# Import control
__all__ = ["AiAPI"]
