from abc import ABC, abstractmethod
from typing import Optional

class AIServiceInterface(ABC):
    @abstractmethod
    def extract_features(self, description, image_path: Optional[str] = None):
        pass

    @abstractmethod
    def ai_semantic_matching(self, input_lost_report, data_list: list):
        pass