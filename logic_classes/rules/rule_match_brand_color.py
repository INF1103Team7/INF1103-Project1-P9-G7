from ..match_rule import MatchRule


class BrandColorMatchRule(MatchRule):

    def is_satisfied(self, data):
        return (
            data["brand_match"] == "match"
            and data["color_match"] == "match"
        )

    def apply_rule(self, score):
        return score + 7.0
    
    def get_rule_name(self):
        return "BRAND_AND_COLOR_MATCH"
    def get_rule_type(self):
            return "positive"
