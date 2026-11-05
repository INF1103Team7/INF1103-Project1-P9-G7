from typing import ClassVar

from ._terms import COLOR_TERMS
from .items import Items


class Bag(Items):
    value: ClassVar[str] = "bag"
    description_guidance: ClassVar[str] = (
        "its color, size, material, or brand, plus a distinctive pocket, strap, "
        "mark, or feature"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "color",
            "colour",
            *COLOR_TERMS,
            "size",
            "material",
            "brand",
            "backpack",
            "tote",
        ),
        ("pocket", "strap", "logo", "sticker", "scratch", "mark", "zipper"),
    )
