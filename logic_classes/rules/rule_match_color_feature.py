from ..match_rule import MatchRule


class ColorFeatureMatchRule(MatchRule):
    def __init__(self, config):
        self.config = config

    def is_satisfied(self, data):
        return (
            data["color_match"] == "match"
            and len(data["feature_overlaps"]) >= self.config.min_feature_strong_match
        )

    def apply_rule(self, score):
        return score + 5.0
    
    def get_rule_name(self):
        return "COLOR_AND_MULTIPLE_FEATURES_MATCH"
    def get_rule_type(self):
            return "positive"
