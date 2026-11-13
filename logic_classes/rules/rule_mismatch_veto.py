from ..match_rule import MatchRule


class VetoMismatchRule(MatchRule):
    def is_satisfied(self, data):
        return (
            data["color_match"] == "not match"
            and data["material_match"] == "not match"
            and len(data["feature_overlaps"]) == 0
        )

    def apply_rule(self, score):
        return min(score, 25.0)
    
    def get_rule_name(self):
        return "CORE_VISUAL_MISMATCH_VETO"
    
    def get_rule_type(self):
        return "veto"