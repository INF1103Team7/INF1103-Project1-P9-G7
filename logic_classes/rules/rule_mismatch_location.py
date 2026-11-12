from ..match_rule import MatchRule


class LocationMismatchRule(MatchRule):
    def __init__(self, config):
        self.config = config

    def is_satisfied(self, data):
        if not self.config.consider_location:
            return False
        return data["location_match"] == "not match"

    def apply_rule(self, score):
        return score - 5.0
    
    def get_rule_name(self):
        return "LOCATION_MISMATCH"
    
    def get_rule_type(self):
        return "negative"