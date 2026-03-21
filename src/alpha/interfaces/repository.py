"""Contains the Repository interface definition."""

from typing import Any, Protocol, runtime_checkable

from alpha.domain.models.base_model import DomainModel


@runtime_checkable
class Repository(Protocol[DomainModel]):
    """Interface for a generic repository."""

    session: Any
    _default_model: DomainModel

    def __init__(self, session: Any, default_model: DomainModel) -> None:
        """Initialize the repository with a session and a default model."""

    def add(
        self,
        obj: DomainModel,
        return_obj: bool = True,
    ) -> DomainModel | None:
        """_summary_"""

    def add_all(
        self,
        objs: list[DomainModel],
        return_obj: bool = False,
    ) -> list[DomainModel] | None:
        """_summary_"""

    def get(
        self,
        model: DomainModel | None = None,
    ) -> DomainModel:
        """_summary_"""
        ...

    def get_all(
        self,
        model: DomainModel | None = None,
    ) -> list[DomainModel]:
        """_summary_"""
        ...

    def patch(self) -> Any:
        """_summary_"""

    def remove(self, obj: DomainModel) -> None:
        """_summary_"""

    def update(self, obj: DomainModel) -> DomainModel:
        """_summary_"""
        ...
