from ..match_rule import MatchRule
class ColorOnlyMatchRule(MatchRule):
    def is_satisfied(self, data):
        return (
            data["color_match"] == "match"
            and data["material_match"] == "not match"
            and data["brand_match"] == "not match"
            and len(data["feature_overlaps"]) == 0
        )

    def apply_rule(self, score):
        return score - 10.0
    
    def get_rule_name(self):
        return "COLOR_ONLY_MATCH"
    
    def get_rule_type(self):
        return "negative"