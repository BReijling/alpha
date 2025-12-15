from typing import Any, ClassVar, Protocol, runtime_checkable


@runtime_checkable
class AttrsInstance(Protocol):
    """Attrs instance interface"""

    __attrs_attrs__: ClassVar[dict[str, Any]]

    def __call__(self, *args: Any, **kwds: Any) -> Any: ...
