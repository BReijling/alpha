from dataclasses import Field
from typing import Any, ClassVar, Protocol, runtime_checkable


@runtime_checkable
class DataclassInstance(Protocol):
    """Dataclass instance interface"""

    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]

    def __call__(self, *args: Any, **kwds: Any) -> Any: ...
