from abc import ABC, abstractmethod
import re
from typing import ClassVar


class Items(ABC):
    """Base class for the supported item categories."""

    description_guidance: ClassVar[str]
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]]

    @property
    @abstractmethod
    def value(self) -> str:
        """Return the category value used by the existing report data format."""

    @classmethod
    def from_value(cls, value: str) -> "Items":
        from . import _ITEM_CLASSES

        for item_class in _ITEM_CLASSES:
            item = item_class()
            if item.value == value:
                return item
        raise ValueError(f"Unsupported item category: {value}")

    def validate_description(self, description: str) -> bool:
        """Require one identifying detail from each category-specific group."""
        tokens = re.findall(r"[a-z0-9]+", description.casefold())
        words = set(tokens)
        normalized_description = " ".join(tokens)

        def matches_term(term: str) -> bool:
            if " " in term:
                return term in normalized_description
            return term in words or (
                len(term) >= 4
                and any(word.startswith(term) for word in words)
            )

        return all(
            any(matches_term(term) for term in detail_group)
            for detail_group in self.identifying_detail_groups
        )
