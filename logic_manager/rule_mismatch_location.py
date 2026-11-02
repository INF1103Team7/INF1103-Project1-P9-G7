from .match_rule import MatchRule
class LocationMismatchRule(MatchRule):

    def is_satisfied(self, data):
        return data["location_match"] == "not match"

    def apply_rule(self, score):
        return score - 5.0
    
    def get_rule_name(self):
        return "LOCATION_MISMATCH"