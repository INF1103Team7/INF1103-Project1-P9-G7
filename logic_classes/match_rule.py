# Abstract base class that defines the required structure and behaviour for all business rule classes.

from abc import ABC, abstractmethod

class MatchRule(ABC):
    # check whether conditions of business rule are satisfied #
    @abstractmethod
    def is_satisfied(self, data):
        pass
    
    # determines how the score is calculated if the rule is satisfied #
    @abstractmethod
    def apply_rule(self, score):
        pass
    
    # returns the name of the business rule #
    @abstractmethod
    def get_rule_name(self):
        pass
    
    # for RuleManager to organize rules by type#
    @abstractmethod
    def get_rule_type(self):
        pass
    
    # Default behaviour: rules are not skipped when a veto is triggered.
    def skip_if_veto_triggered(self):
        return False