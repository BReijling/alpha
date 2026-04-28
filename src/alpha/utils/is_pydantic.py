from typing import Any


def is_pydantic(obj: Any) -> bool:
    """Validates if an object is a pydantic class or instance

    Parameters
    ----------
    obj
        An object which will be checked to be a pydantic class or instance

    Returns
    -------
    bool
        Returns True if obj is a pydantic class or instance
    """
    cls = obj if isinstance(obj, type) else type(obj)

    for base_class in getattr(cls, "__mro__", ()):  # pragma: no branch
        try:
            if "__pydantic_fields__" in vars(base_class):
                return True
        except TypeError:
            continue

    return False
