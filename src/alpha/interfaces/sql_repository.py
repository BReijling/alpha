"""_summary_"""

from enum import Enum
from typing import Any, Literal, Protocol, overload, runtime_checkable
from uuid import UUID

from sqlalchemy.orm import (
    Query,
    Session,
)
from sqlalchemy.orm.attributes import InstrumentedAttribute

from alpha.domain.models.base_model import BaseDomainModel, DomainModel
from alpha.infra.models.search_filter import SearchFilter
from alpha.infra.models.query_clause import QueryClause
from alpha.interfaces.patchable import Patchable
from alpha.interfaces.updateable import Updateable


@runtime_checkable
class SqlRepository(Protocol[DomainModel]):
    """_summary_

    Parameters
    ----------
    Protocol : _type_
        _description_
    """

    session: Session
    _default_model: DomainModel

    def __init__(self, session: Session, default_model: DomainModel) -> None:
        """_summary_

        Parameters
        ----------
        session : Session
            _description_
        default_model : DomainModel
            _description_
        """

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
        """_summary_

        Parameters
        ----------
        obj : DomainModel
            _description_
        raise_if_exists : bool, optional
            _description_, by default False
        """

    def add_all(
        self,
        objs: list[DomainModel],
        return_obj: bool = False,
        raise_if_exists: bool = False,
    ) -> list[DomainModel] | None:
        """_summary_

        Parameters
        ----------
        objs : list[DomainModel]
            _description_
        raise_if_exists : bool, optional
            _description_, by default False
        """

    def count(
        self,
        model: DomainModel | None = None,
        **kwargs: Any,
    ) -> int:
        """_summary_

        Parameters
        ----------
        model : DomainModel | None, optional
            _description_, by default None

        Returns
        -------
        int
            _description_
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
        """_summary_

        Parameters
        ----------
        attr : str | InstrumentedAttribute
            _description_
        value : str | int | float | Enum | UUID
            _description_
        cursor_result : str, optional
            _description_, by default "first"
        model : DomainModel | None, optional
            _description_, by default None

        Returns
        -------
        DomainModel
            _description_
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
        """_summary_

        Parameters
        ----------
        attr : str | InstrumentedAttribute
            _description_
        value : str | int | float | Enum | UUID
            _description_
        cursor_result : str, optional
            _description_, by default "all"
        model : DomainModel | None, optional
            _description_, by default None

        Returns
        -------
        list[DomainModel]
            _description_
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
        """_summary_

        Parameters
        ----------
        attr : str | InstrumentedAttribute
            _description_
        value : str | int | float | Enum | UUID
            _description_
        cursor_result : str, optional
            _description_, by default "one"
        model : DomainModel | None, optional
            _description_, by default None

        Returns
        -------
        DomainModel
            _description_
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
        """_summary_

        Parameters
        ----------
        attr : str | InstrumentedAttribute
            _description_
        value : str | int | float | Enum | UUID
            _description_
        cursor_result : str, optional
            _description_, by default "one_or_none"
        model : DomainModel | None, optional
            _description_, by default None

        Returns
        -------
        DomainModel | None
            _description_
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
        """_summary_

        Parameters
        ----------
        value : str | int | UUID
            _description_
        attr : str | InstrumentedAttribute, optional
            _description_, by default "id"
        cursor_result : str, optional
            _description_, by default "one_or_none"
        model : DomainModel | None, optional
            _description_, by default None

        Returns
        -------
        DomainModel | None
            _description_
        """
        ...

    def patch(self, obj: Patchable, patches: dict[str, Any]) -> DomainModel:
        """_summary_

        Parameters
        ----------
        obj : Patchable
            _description_
        patches : dict[str, Any]
            _description_

        Returns
        -------
        DomainModel
            _description_
        """

    def remove(self, obj: DomainModel) -> None:
        """_summary_

        Parameters
        ----------
        obj : DomainModel
            _description_
        """

    def remove_all(
        self,
        objs: list[DomainModel] | None,
        **kwargs: Any,
    ) -> None:
        """_summary_

        Parameters
        ----------
        objs : list[DomainModel] | None
            _description_
        """

    def select(
        self,
        model: DomainModel | None = None,
        cursor_result: str = "all",
        **kwargs: Any,
    ) -> list[DomainModel]:
        """_summary_

        Parameters
        ----------
        model : DomainModel | None, optional
            _description_, by default None
        cursor_result : str, optional
            _description_, by default "all"

        Returns
        -------
        list[DomainModel]
            _description_
        """
        ...

    def update(self, obj: Updateable, other: DomainModel) -> DomainModel:
        """_summary_

        Parameters
        ----------
        obj : DomainModel
            _description_
        other : DomainModel
            _description_

        Returns
        -------
        DomainModel
            _description_
        """
        ...

    def view(
        self,
        model: DomainModel,
        cursor_result: str = "all",
        **kwargs: Any,
    ) -> list[DomainModel]:
        """_summary_

        Parameters
        ----------
        model : DomainModel
            _description_
        cursor_result : str, optional
            _description_, by default "all"

        Returns
        -------
        list[DomainModel]
            _description_
        """
        ...

    def _query(
        self,
        cursor_result: str | None = None,
        model: DomainModel | None = None,
        filters: list[SearchFilter] = [],
        **kwargs: Any,
    ) -> Any:
        """_summary_

        Parameters
        ----------
        cursor_result : str | None, optional
            _description_, by default None
        model : DomainModel | None, optional
            _description_, by default None
        filters : list[SearchFilter], optional
            _description_, by default []

        Returns
        -------
        Any
            _description_
        """
        ...

    def _query_clause(
        self,
        clause: QueryClause,
        query: Query[Any],
        model: DomainModel,
    ) -> Query[Any]: ...
