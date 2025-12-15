from typing import Any, ClassVar, Protocol, runtime_checkable


@runtime_checkable
class OpenAPIModel(Protocol):
    """OpenAPIModel interface"""

    openapi_types: ClassVar[dict[str, type]]
    attribute_map: ClassVar[dict[str, str]]

    def __init__(self) -> None: ...

    def to_dict(self) -> dict[str, Any]: ...

    def to_str(self): ...

    def __repr__(self): ...

    def __eq__(self, other): ...

    def __ne__(self, other): ...
