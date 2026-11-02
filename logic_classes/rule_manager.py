class RuleManager:
    def __init__(self):
        self.veto_rules = []
        self.negative_rules = []
        self.positive_rules = []
        self.bonus_rules = []

    def add_rule(self, rule):
        categories = {
            "veto": self.veto_rules,
            "negative": self.negative_rules,
            "positive": self.positive_rules,
            "bonus": self.bonus_rules
        }
        category = rule.get_rule_type()

        if category not in categories:
            raise ValueError("Invalid rule category")

        categories[category].append(rule)

    def __apply_rules(self, rules, data, score, triggered_rules_list):
        for rule in rules:
            if rule.is_satisfied(data):
                triggered_rules_list.append(rule.get_rule_name())
                score = rule.apply_rule(score)

        return score

    def evaluate(self, data, score):
        triggered_rules_list = []
        veto_triggered = False
        positive_rule = None

        # 1. Veto Rules
        for rule in self.veto_rules:
            if rule.is_satisfied(data):
                veto_triggered = True
                triggered_rules_list.append(rule.get_rule_name())
                score = rule.apply_rule(score)

        # 2. Negative Rules
        for rule in self.negative_rules:

            if (
                veto_triggered
                and rule.get_rule_name() == "COLOR_AND_MATERIAL_MISMATCH"
            ):
                continue

            if rule.is_satisfied(data):
                triggered_rules_list.append(rule.get_rule_name())
                score = rule.apply_rule(score)
    
        # 3. Positive Rules
        for rule in self.positive_rules:
            if rule.is_satisfied(data):
                positive_rule = rule.get_rule_name()
                triggered_rules_list.append(positive_rule)
                score = rule.apply_rule(score)
                break

        # 4. Bonus Rules
        score = self.__apply_rules(
            self.bonus_rules, data, score, triggered_rules_list
        )

        # 5. Final Score
        score = max(0.0, min(score, 100.0))

        return {
            "final_score": score,
            "triggered_rules_list": triggered_rules_list,
            "veto_triggered": veto_triggered,
            "positive_rule": positive_rule
        }