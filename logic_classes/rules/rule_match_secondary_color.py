from ..match_rule import MatchRule


class SecondaryColorMatchRule(MatchRule):

    def is_satisfied(self, data):
        color_data = data["color_data"]

        return (
            isinstance(color_data, dict)
            and "secondary" in color_data
            and data["color_match"] == "match"
        )

    def apply_rule(self, score):
        return score + 3.0

    def get_rule_name(self):
        return "PRIMARY_SECONDARY_COLOR_MATCH"
    
    def get_rule_type(self):
        return "bonus"