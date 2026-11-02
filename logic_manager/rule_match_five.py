from .match_rule import MatchRule
class FullMatchRule(MatchRule):
    def __init__(self, config):
        self.config = config

    def is_satisfied(self, data):
        return (
            data["brand_match"] == "match"
            and data["color_match"] == "match"
            and data["material_match"] == "match"
            and data["location_match"] == "match"
            and len(data["feature_overlaps"]) >= self.config.get_min_feature_excellent_match()
        )

    def apply_rule(self, score):
        return score + 10.0
    
    def get_rule_name(self):
        return "ALL_MAJOR_ATTRIBUTES_AND_LOCATION_MATCH"
