from .bag import Bag
from .bottle import Bottle
from .clothing import Clothing
from .electronics import Electronics
from .items import Items
from .keys import Keys
from .other_item import OtherItem
from .student_card import StudentCard

_ITEM_CLASSES = (
    StudentCard,
    Bottle,
    Keys,
    Bag,
    Clothing,
    Electronics,
    OtherItem,
)
CATEGORIES = tuple(item_class.value for item_class in _ITEM_CLASSES)

__all__ = [
    "Bag",
    "Bottle",
    "CATEGORIES",
    "Clothing",
    "Electronics",
    "Items",
    "Keys",
    "OtherItem",
    "StudentCard",
]
