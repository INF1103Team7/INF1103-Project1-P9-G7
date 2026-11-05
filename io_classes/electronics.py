from typing import ClassVar

from ._terms import COLOR_TERMS
from .items import Items


class Electronics(Items):
    value: ClassVar[str] = "electronics"
    description_guidance: ClassVar[str] = (
        "the device type, brand, model, or color, plus a distinctive case, "
        "mark, or feature (do not include serial numbers)"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "phone",
            "laptop",
            "tablet",
            "earbuds",
            "headphones",
            "watch",
            "brand",
            "model",
            "color",
            "colour",
            *COLOR_TERMS,
        ),
        ("case", "sticker", "scratch", "mark", "screen", "button", "crack", "shape"),
    )
