"""Provide the supported item categories for report collection."""
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
    def categories(cls):
        """Returns the supported item categories tuple."""
        return cls._CATEGORIES
