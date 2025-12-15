from typing import Any


def is_attrs(obj: Any) -> bool:
    """Validates if an object is an attrs class or instance

    Parameters
    ----------
    obj : Any
        An object which will be checked to be an attrs class or instance

    Returns
    -------
    bool
        Returns True if obj is an attrs class or instance
    """
    cls = obj if isinstance(obj, type) else type(obj)
    return hasattr(cls, '__attrs_attrs__')
