# Imports
from google.genai import types

# Class to manage AI configuration settings, including models, temperature, and timeout.
class AiConfiguration:
    # Initialise the AI configuration with default values for models, temperature, and timeout.
    def __init__(self):
        self._models = [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash"
        ]
        self._temperature = 0.1
        self._timeout = 90000

        # AI conguration
        self._config = types.GenerateContentConfig (
            response_mime_type = "application/json",
            temperature = self._temperature,
            automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True),
            # Set request timeout 30 seconds
            http_options = types.HttpOptions(timeout = self._timeout)
        )

    # Property getters for models and config to allow access to these attributes from outside the class.
    @property
    def models(self):
        return self._models

    @property
    def config(self):
        return self._config

# Import control
__all__ = ["AiConfiguration"]
