from pydantic.fields import FieldInfo
from typing import ClassVar, Protocol, runtime_checkable


@runtime_checkable
class PydanticInstance(Protocol):
    """Pydantic instance interface"""

    __pydantic_fields__: ClassVar[dict[str, FieldInfo]]
