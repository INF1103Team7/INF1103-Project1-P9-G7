from .match_rule import MatchRule
class BrandFeatureMatchRule(MatchRule):
    def __init__(self, config):
        self.config = config

    def is_satisfied(self, data):
        return (
            data["brand_match"] == "match"
            and len(data["feature_overlaps"]) >= self.config.get_min_feature_strong_match()
        )

    def apply_rule(self, score):
        return score + 8.0
    
    def get_rule_name(self):
        return "BRAND_AND_MULTIPLE_FEATURES_MATCH"
