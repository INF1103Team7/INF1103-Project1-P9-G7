from .bag import Bag
from .bottle import Bottle
from .clothing import Clothing
from .electronics import Electronics
from .items import Items
from .keys import Keys
from .other_item import OtherItem
from .formatting import Format
from .print_menu import PrintMenu
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
    "Format",
    "Items",
    "Keys",
    "OtherItem",
    "PrintMenu",
    "StudentCard",
]
