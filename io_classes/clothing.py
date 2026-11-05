from typing import ClassVar

from ._terms import COLOR_TERMS
from .items import Items


class Clothing(Items):
    value: ClassVar[str] = "clothing"
    description_guidance: ClassVar[str] = (
        "the garment, color, pattern, or material, plus a distinctive logo, "
        "mark, or feature"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "shirt",
            "jacket",
            "pants",
            "trousers",
            "hoodie",
            "coat",
            "color",
            "colour",
            *COLOR_TERMS,
            "pattern",
            "material",
        ),
        ("logo", "stain", "tear", "mark", "zipper", "button", "pocket", "design"),
    )
