import json
import os

# store user edited thresholds in a JSON file for persistence across sessions#
class ThresholdFile:
    def __init__(self, filename="threshold_config.json"):
        self.filename = filename

    def save(self, config):
        data = {
            "high_threshold": config.get_high_threshold(),
            "reject_threshold": config.get_reject_threshold(),
            "min_feature_strong_match": config.get_min_feature_strong_match(),
            "min_feature_excellent_match": config.get_min_feature_excellent_match(),
        }

        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)

        return "Thresholds saved successfully."

    def load(self):
        if not os.path.exists(self.filename):
            return None

        with open(self.filename, "r") as file:
            return json.load(file)