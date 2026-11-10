# Item class to handle item categories and related functionalities
class Items:
    _CATEGORIES = (
        "student card",
        "bottle",
        "keys",
        "bag",
        "clothing",
        "electronics",
        "others",
    )

    @classmethod
    def categories(cls) -> tuple[str, ...]: # Returns the supported item categories tuple.
        return cls._CATEGORIES
