from .match_rule import MatchRule
class BrandColorMaterialMatchRule(MatchRule):
    def is_satisfied(self, data):
        return (
            data["brand_match"] == "match"
            and data["color_match"] == "match"
            and data["material_match"] == "match"
        )

    def apply_rule(self, score):
        return score + 10.0
    
    def get_rule_name(self):
        return "COLOR_MATERIAL_BRAND_MATCH"
