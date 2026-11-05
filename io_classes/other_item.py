from typing import ClassVar

from ._terms import COLOR_TERMS, MATERIAL_TERMS
from .items import Items


class OtherItem(Items):
    value: ClassVar[str] = "others"
    description_guidance: ClassVar[str] = (
        "its type, color, material, or shape, plus a distinctive mark or feature"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "type",
            "color",
            "colour",
            *COLOR_TERMS,
            "material",
            *MATERIAL_TERMS,
            "shape",
            "brand",
            "size",
        ),
        ("sticker", "scratch", "mark", "pattern", "damage", "label", "feature"),
    )
