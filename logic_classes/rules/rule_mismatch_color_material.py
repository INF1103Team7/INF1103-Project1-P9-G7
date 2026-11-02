from ..match_rule import MatchRule

class ColorMaterialMismatchRule(MatchRule):
    def is_satisfied(self, data):
        return (
            data["color_match"] == "not match"
            and data["material_match"] == "not match"
        )

    def apply_rule(self, score):
        return score - 10.0
    
    def get_rule_name(self):
        return "COLOR_AND_MATERIAL_MISMATCH"
    
    def get_rule_type(self):
        return "negative"