from typing import Any


def is_pydantic(obj: Any) -> bool:
    """Validates if an object is a pydantic class or instance

    Parameters
    ----------
    obj : Any
        An object which will be checked to be a pydantic class or instance

    Returns
    -------
    bool
        Returns True if obj is a pydantic class or instance
    """
    cls = obj if isinstance(obj, type) else type(obj)
    return hasattr(cls, '__pydantic_fields__')
