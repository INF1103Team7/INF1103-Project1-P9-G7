from ..match_rule import MatchRule
class BrandColorFeatureMatchRule(MatchRule):
    def __init__(self, config):
        self.config = config

    def is_satisfied(self, data):
        return (
            data["brand_match"] == "match"
            and data["color_match"] == "match"
            and len(data["feature_overlaps"]) >= self.config.get_min_feature_strong_match()
        )

    def apply_rule(self, score):
        return score + 10.0
    
    def get_rule_name(self):
        return "BRAND_COLOR_FEATURE_MATCH"
    def get_rule_type(self):
            return "positive"
