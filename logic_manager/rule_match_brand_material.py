from .match_rule import MatchRule
class BrandMaterialMatchRule(MatchRule):
    def is_satisfied(self, data):
        return (
            data["brand_match"] == "match"
            and data["material_match"] == "match"
        )

    def apply_rule(self, score):
        return score + 7.0
    
    def get_rule_name(self):
        return "BRAND_AND_MATERIAL_MATCH"
