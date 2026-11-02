# every business rule class must provide its own implementation of them #
from abc import ABC, abstractmethod
class MatchRule(ABC):
    @abstractmethod
    def is_satisfied(self, data):
        pass

    @abstractmethod
    def apply_rule(self, score):
        pass
    
    @abstractmethod
    def get_rule_name(self):
        pass
    
    @abstractmethod
    def get_rule_type(self):
        pass