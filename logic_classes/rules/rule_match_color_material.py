from ..match_rule import MatchRule
class ColorMaterialMatchRule(MatchRule):
    def is_satisfied(self, data):
        return (
            data["color_match"] == "match"
            and data["material_match"] == "match"
        )

    def apply_rule(self, score):
        return score + 5.0
    
    def get_rule_name(self):
        return "COLOR_AND_MATERIAL_MATCH"
    def get_rule_type(self):
            return "positive"