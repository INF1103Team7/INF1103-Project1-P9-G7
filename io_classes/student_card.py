from typing import ClassVar

from ._terms import COLOR_TERMS
from .items import Items


class StudentCard(Items):
    value: ClassVar[str] = "student card"
    description_guidance: ClassVar[str] = (
        "the card's appearance or issuer (not its number), plus a distinctive "
        "visible feature"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "color",
            "colour",
            *COLOR_TERMS,
            "school",
            "sit",
            "design",
            "holder",
            "lanyard",
        ),
        ("sticker", "scratch", "damage", "pattern", "mark", "chip", "crease", "logo"),
    )
