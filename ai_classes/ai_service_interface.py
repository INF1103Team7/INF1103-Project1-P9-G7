# Imports
from abc import ABC, abstractmethod
from typing import Optional

# Base abstract class for core functions of AI service
class AIServiceInterface(ABC):
    @abstractmethod
    def extract_features(self, description: str, image_path: Optional[str] = None) -> dict:
        pass

    @abstractmethod
    def ai_semantic_matching(self, input_lost_report: str, data_list: list) -> list:
        pass

# Import control
__all__ = ["AIServiceInterface"]
