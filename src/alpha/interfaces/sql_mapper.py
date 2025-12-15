"""_summary_
"""
from typing import Any, ClassVar, Protocol, runtime_checkable

import sqlalchemy as sa
from sqlalchemy.orm import registry


@runtime_checkable
class SqlMapper(Protocol):
    """_summary_"""

    convention: ClassVar[dict[str, Any]]
    started: ClassVar[bool]
    schema_name: ClassVar[str]

    metadata: ClassVar[sa.MetaData]

    mapper_registry: ClassVar[registry]

    @classmethod
    def start_mapping(cls) -> None:
        """_summary_"""
