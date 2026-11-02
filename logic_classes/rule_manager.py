class RuleManager:
    """
    Manages and evaluates business rules by grouping them according to their categories.
    """

    def __init__(self):
        # Store rule objects in separate lists based on their categories.
        self.veto_rules = []
        self.negative_rules = []
        self.positive_rules = []
        self.bonus_rules = []

    def add_rule(self, rule):
        # Map each rule category to its corresponding list.
        categories = {
            "veto": self.veto_rules,
            "negative": self.negative_rules,
            "positive": self.positive_rules,
            "bonus": self.bonus_rules
        }

        # Retrieve the category defined by the rule object.
        category = rule.get_rule_type()

        # Reject rules that do not belong to a recognised category.
        if category not in categories:
            raise ValueError("Invalid rule category")

        # Add the rule object to the appropriate category list.
        categories[category].append(rule)

    def __apply_rules(self, rules, data, score, triggered_rules_list):
        # Apply every rule in the supplied list if its conditions are satisfied.
        for rule in rules:
            if rule.is_satisfied(data):
                # Record the name of the rule that was triggered.
                triggered_rules_list.append(rule.get_rule_name())

                # Apply the rule's scoring adjustment.
                score = rule.apply_rule(score)

        return score

    def evaluate(self, data, score):
        # Store the names of all rules that are triggered during evaluation.
        triggered_rules_list = []
        veto_triggered = False
        positive_rule = None

        # 1. Veto Rules
        # Evaluate all veto rules and apply their scoring adjustments.
        for rule in self.veto_rules:
            if rule.is_satisfied(data):
                veto_triggered = True
                triggered_rules_list.append(rule.get_rule_name())
                score = rule.apply_rule(score)

        # 2. Negative Rules
        # Evaluate negative rules, with a special exception when a veto is triggered.
        for rule in self.negative_rules:

            # Skip this specific negative rule if a veto rule has already been triggered.
            if (
                veto_triggered
                and rule.get_rule_name() == "COLOR_AND_MATERIAL_MISMATCH"
            ):
                continue

            if rule.is_satisfied(data):
                triggered_rules_list.append(rule.get_rule_name())
                score = rule.apply_rule(score)

        # 3. Positive Rules
        # Apply only the first positive rule whose conditions are satisfied.
        for rule in self.positive_rules:
            if rule.is_satisfied(data):
                positive_rule = rule.get_rule_name()
                triggered_rules_list.append(positive_rule)
                score = rule.apply_rule(score)
                break

        # 4. Bonus Rules
        # Apply all bonus rules whose conditions are satisfied.
        score = self.__apply_rules(
            self.bonus_rules, data, score, triggered_rules_list
        )

        # 5. Final Score
        # Keep the final score within the range of 0 to 100.
        score = max(0.0, min(score, 100.0))

        # Return the final score and details about the triggered rules.
        return {
            "final_score": score,
            "triggered_rules_list": triggered_rules_list,
            "veto_triggered": veto_triggered,
            "positive_rule": positive_rule
        }