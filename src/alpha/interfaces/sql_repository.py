"""Contains the SqlRepository protocol, which defines the interface for
SQLAlchemy ORM repository operations.
"""

from enum import Enum
from typing import Any, Literal, Protocol, overload, runtime_checkable
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from alpha.domain.models.base_model import BaseDomainModel, DomainModel
from alpha.infra.models.json_patch import JsonPatch
from alpha.interfaces.patchable import Patchable
from alpha.interfaces.updatable import Updatable


@runtime_checkable
class SqlRepository(Protocol[DomainModel]):
    """Repository interface for SQLAlchemy ORM operations.

    Generic
    -------
        A generic type variable used to specify the domain model type for the
        repository.
    """

    session: Session
    _default_model: DomainModel

    @overload
    def add(
        self,
        obj: DomainModel,
        return_obj: Literal[True] = True,
        raise_if_exists: bool = False,
    ) -> DomainModel: ...

    @overload
    def add(
        self,
        obj: DomainModel,
        return_obj: Literal[False],
        raise_if_exists: bool = False,
    ) -> None: ...

    def add(
        self,
        obj: DomainModel,
        return_obj: bool = True,
        raise_if_exists: bool = False,
    ) -> DomainModel | None:
        """Add a domain model instance to the database.

        Parameters
        ----------
        obj
            The domain model instance to add to the database.
        raise_if_exists
            Whether to raise an exception if the instance already exists, by
            default False
        """
        ...

    def add_all(
        self,
        objs: list[DomainModel],
        return_obj: bool = False,
        raise_if_exists: bool = False,
    ) -> list[DomainModel] | None:
        """Add multiple domain model instances to the database.

        Parameters
        ----------
        objs
            The list of domain model instances to add to the database.
        raise_if_exists
            Whether to raise an exception if any of the instances already exist, by default False
        """
        ...

    def count(
        self,
        model: DomainModel | None = None,
        **kwargs: Any,
    ) -> int:
        """Count the number of domain model instances in the database.

        Parameters
        ----------
        model
            The domain model class to count instances of, by default None

        Returns
        -------
        int
            The number of domain model instances in the database.
        """
        ...

    def get(
        self,
        attr: str | InstrumentedAttribute[Any],
        value: str | int | float | Enum | UUID | BaseDomainModel,
        cursor_result: str = "first",
        model: DomainModel | None = None,
        **kwargs: Any,
    ) -> DomainModel:
        """Retrieve a single domain model instance from the database based on a
        specific attribute and value.

        Parameters
        ----------
        attr
            The attribute to filter by.
        value
            The value of the attribute to filter by.
        cursor_result
            The type of result to return, by default "first"
        model
            The domain model class to query, by default None

        Returns
        -------
        DomainModel
            The domain model instance that matches the query, or None if no
            match is found.
        """
        ...

    def get_all(
        self,
        attr: str | InstrumentedAttribute[Any],
        value: str | int | float | Enum | UUID | BaseDomainModel,
        cursor_result: str = "all",
        model: DomainModel | None = None,
        **kwargs: Any,
    ) -> list[DomainModel]:
        """Retrieve multiple domain model instances from the database based on
        a specific attribute and value.

        Parameters
        ----------
        attr
            The attribute to filter by.
        value
            The value of the attribute to filter by.
        cursor_result
            The type of result to return, by default "all"
        model
            The domain model class to query, by default None

        Returns
        -------
        list[DomainModel]
            The list of domain model instances that match the query.
        """
        ...

    def get_one(
        self,
        attr: str | InstrumentedAttribute[Any],
        value: str | int | float | Enum | UUID,
        cursor_result: str = "one",
        model: DomainModel | None = None,
        **kwargs: Any,
    ) -> DomainModel:
        """Retrieve a single domain model instance from the database based on a
        specific attribute and value, ensuring that exactly one match is found.

        Parameters
        ----------
        attr
            The attribute to filter by.
        value
            The value of the attribute to filter by.
        cursor_result
            The type of result to return, by default "one"
        model
            The domain model class to query, by default None

        Returns
        -------
        DomainModel
            The domain model instance that matches the query, or None if no
            match is found.
        """
        ...

    def get_one_or_none(
        self,
        attr: str | InstrumentedAttribute[Any],
        value: str | int | float | Enum | UUID,
        cursor_result: str = "one_or_none",
        model: DomainModel | None = None,
        **kwargs: Any,
    ) -> DomainModel | None:
        """Retrieve a single domain model instance from the database based on a
        specific attribute and value, ensuring that at most one match is found.

        Parameters
        ----------
        attr
            The attribute to filter by.
        value
            The value of the attribute to filter by.
        cursor_result
            The type of result to return, by default "one_or_none"
        model
            The domain model class to query, by default None

        Returns
        -------
        DomainModel | None
            The domain model instance that matches the query, or None if no
            match is found.
        """
        ...

    def get_by_id(
        self,
        value: str | int | UUID,
        attr: str | InstrumentedAttribute[Any] = "id",
        cursor_result: str = "one_or_none",
        model: DomainModel | None = None,
        **kwargs: Any,
    ) -> DomainModel | None:
        """Retrieve a single domain model instance from the database based on
        its unique identifier.

        Parameters
        ----------
        value
            The unique identifier of the domain model instance.
        attr
            The attribute to filter by, by default "id"
        cursor_result
            The type of result to return, by default "one_or_none"
        model
            The domain model class to query, by default None

        Returns
        -------
        DomainModel | None
            The domain model instance that matches the query, or None if no
            match is found.
        """
        ...

    def patch(self, obj: Patchable[Any], patches: JsonPatch) -> DomainModel:
        """Patch a domain model instance in the database using a JSON patch
        object.

        Parameters
        ----------
        obj
            The domain model instance to patch.
        patches
            The JSON patch object containing the changes to apply to the domain
            model instance.

        Returns
        -------
        DomainModel
            The patched domain model instance.
        """
        ...

    def remove(self, obj: DomainModel) -> None:
        """Remove a domain model instance from the database.

        Parameters
        ----------
        obj
            The domain model instance to remove.
        """
        ...

    def remove_all(
        self,
        objs: list[DomainModel] | None,
        **kwargs: Any,
    ) -> None:
        """Remove multiple domain model instances from the database.

        Parameters
        ----------
        objs
            The list of domain model instances to remove, by default None
        """
        ...

    def select(
        self,
        model: DomainModel | None = None,
        cursor_result: str = "all",
        **kwargs: Any,
    ) -> list[DomainModel]:
        """Select domain model instances from the database based on optional
        filters.

        Parameters
        ----------
        model
            The domain model class to query, by default None
        cursor_result
            The type of result to return, by default "all"

        Returns
        -------
        list[DomainModel]
            The list of domain model instances that match the query.
        """
        ...

    def update(self, obj: Updatable, other: DomainModel) -> DomainModel:
        """Update a domain model instance in the database.

        Parameters
        ----------
        obj
            The domain model instance to update.

        other
            The domain model instance containing the updated values.

        Returns
        -------
        DomainModel
            The updated domain model instance.
        """
        ...

    def view(
        self,
        model: DomainModel,
        cursor_result: str = "all",
        **kwargs: Any,
    ) -> list[DomainModel]:
        """View domain model instances from the database based on optional
        filters.


        Parameters
        ----------
        model
            The domain model class to query.
        cursor_result
            The type of result to return, by default "all"

        Returns
        -------
        list[DomainModel]
            The list of domain model instances that match the query.
        """
        ...
