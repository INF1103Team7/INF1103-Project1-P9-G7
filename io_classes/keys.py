from typing import ClassVar

from ._terms import COLOR_TERMS
from .items import Items


class Keys(Items):
    value: ClassVar[str] = "keys"
    description_guidance: ClassVar[str] = (
        "the keys or keychain, plus a distinctive tag, fob, color, or mark"
    )
    identifying_detail_groups: ClassVar[tuple[tuple[str, ...], ...]] = (
        (
            "key",
            "keys",
            "keychain",
            "key chain",
            "ring",
            "metal",
            "number",
            *COLOR_TERMS,
        ),
        (
            "tag",
            "fob",
            "charm",
            "color",
            "colour",
            *COLOR_TERMS,
            "scratch",
            "mark",
            "shape",
        ),
    )
