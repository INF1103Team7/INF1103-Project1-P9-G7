class RuleManager:
    def __init__(self):
        self.veto_rules = []
        self.negative_rules = []
        self.positive_rules = []
        self.bonus_rules = []

    def add_rule(self, rule, category):
        if category == "veto":
            self.veto_rules.append(rule)
        elif category == "negative":
            self.negative_rules.append(rule)
        elif category == "positive":
            self.positive_rules.append(rule)
        elif category == "bonus":
            self.bonus_rules.append(rule)

    def evaluate(self, data, score):
        triggered_rules = []
        veto_triggered = False        
        for rule in self.veto_rules:
            if rule.is_satisfied(data):
                veto_triggered = True
                triggered_rules.append(rule.get_rule_name())
                score = rule.apply_rule(score)
        for rule in self.negative_rules:
            if rule.is_satisfied(data):
                pass
        return score