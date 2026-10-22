from typing import Any


class ToDictMixin:
    """This mixin provides a method to convert a domain model instance to a
    dictionary. It handles various attribute storage mechanisms and ensures
    that all relevant attributes are included in the resulting dictionary.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert the domain model instance to a dictionary.

        This method inspects the instance for various attribute storage
        mechanisms, including dataclass fields, attrs attributes, Pydantic
        fields, __dict__, and __slots__, and collects all non-private
        attributes into a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation of the domain model instance.
        """
        obj: dict[str, Any] = {}

        attributes: list[str] = []

        if hasattr(self, "__dataclass_fields__"):
            attributes = getattr(self, "__dataclass_fields__").keys()
        elif hasattr(self, "__attrs_attrs__"):
            attributes = [
                field.name for field in getattr(self, "__attrs_attrs__")
            ]
        elif hasattr(self, "__pydantic_fields__"):
            attributes = getattr(self, "__pydantic_fields__").keys()
        else:
            attributes = list(getattr(self, "__dict__", {}).keys())
            for cls in type(self).__mro__:
                slots = cls.__dict__.get("__slots__", ())
                if isinstance(slots, str):
                    slots = (slots,)
                attributes.extend(
                    slot for slot in slots if hasattr(self, slot)
                )

        for attr in attributes:
            if not attr.startswith("_"):
                obj[attr] = getattr(self, attr)
            if attr == "_id":
                obj[attr] = str(getattr(self, attr))
        return obj
