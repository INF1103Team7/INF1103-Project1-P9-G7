from typing import ClassVar

from ._terms import COLOR_TERMS, MATERIAL_TERMS
from .items import Items


class Bottle(Items):
    value: ClassVar[str] = "bottle"
    description_guidance: ClassVar[str] = (
        "its color, material, brand, or lid, plus a distinctive mark or feature"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "color",
            "colour",
            *COLOR_TERMS,
            "material",
            *MATERIAL_TERMS,
            "brand",
            "lid",
            "cap",
            "size",
            "metal",
        ),
        ("dent", "scratch", "sticker", "logo", "mark", "handle", "pattern"),
    )
