"""Contains the SqlAlchemyRepository implementation which provides
basic CRUD operations for domain models using SqlAlchemy."""

import json
import logging
from enum import Enum
from typing import Any, Generic, Iterable, cast
from uuid import UUID

from sqlalchemy import BinaryExpression, ColumnElement, ColumnOperators
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    Query,
    Session,
)
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import UnaryExpression

from alpha import exceptions
from alpha.domain.models.base_model import (
    BaseDomainModel,
    DomainModel,
)
from alpha.encoder import JSONEncoder
from alpha.infra.models.order_by import OrderBy
from alpha.infra.models.search_filter import SearchFilter
from alpha.infra.models.query_clause import QueryClause
from alpha.infra.models.filter_operators import FilterOperator
from alpha.infra.models.json_patch import JsonPatch
from alpha.interfaces.updateable import Updateable
from alpha.utils.logging_level_checker import logging_level_checker as llc


class SqlAlchemyRepository(Generic[DomainModel]):
    """SqlAlchemy repository implementation. Provides basic CRUD operations for
    domain models.

    The repository uses a SqlAlchemy session to interact with the database. It
    requires a default domain model type to be specified which will be used
    for operations where no specific model type is provided. The following
    operations are supported:
        - add
        - add_all
        - count
        - get
        - get_all
        - get_one
        - get_one_or_none
        - get_by_id
        - patch
        - remove
        - remove_all
        - select
        - update
        - view

    You can also extend this repository to add custom methods by inheriting
    from it and adding your own methods.

    Example:
    ```python
    class CustomRepository(SqlAlchemyRepository[MyDomainModel]):
        def custom_method(self, param: str) -> list[MyDomainModel]:
            # Custom query logic here
            pass
    ```
    """

    def __init__(self, session: Session, default_model: DomainModel) -> None:
        """_summary_

        Parameters
        ----------
        session : Session
            _description_
        default_model : DomainModel
            _description_
        """
        self.session = session
        self._default_model = default_model

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
        return_obj : bool, optional
            _description_, by default True
        raise_if_exists : bool, optional
            _description_, by default False

        Returns
        -------
        DomainModel | None
            _description_

        Raises
        ------
        exceptions.AlreadyExistsException
            _description_
        """
        try:
            self.session.add(obj)
            self.session.flush()
            if return_obj:
                self.session.refresh(obj)
            if llc("debug"):
                logging.debug(
                    "added object to database session: %s",
                    json.dumps(obj, cls=JSONEncoder),
                )
                logging.debug("flushed pending transaction to session")
            if return_obj:
                if llc("debug"):
                    logging.debug(
                        "refreshed object: %s",
                        json.dumps(obj, cls=JSONEncoder),
                    )
                return obj
        except IntegrityError as exc:
            self.session.rollback()
            if llc("debug"):
                logging.debug("rolled back pending transaction from session")
            if raise_if_exists:
                raise exceptions.AlreadyExistsException(exc)
        return None

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
        return_obj : bool, optional
            _description_, by default False
        raise_if_exists : bool, optional
            _description_, by default False

        Returns
        -------
        list[DomainModel] | None
            _description_

        Raises
        ------
        exceptions.AlreadyExistsException
            _description_
        """
        if return_obj:
            objects: list[DomainModel] | None = []
            for obj in objs:
                object_ = self.add(
                    obj=obj,
                    return_obj=return_obj,
                    raise_if_exists=raise_if_exists,
                )
                objects.append(object_)  # type: ignore
            return objects
        try:
            self.session.bulk_save_objects(objs)
            if llc("debug"):
                logging.debug(
                    "bulk added objects to database session: %s",
                    json.dumps(objs, cls=JSONEncoder),
                )
            self.session.flush()
            if llc("debug"):
                logging.debug("flushed pending transactions to session")
        except IntegrityError as exc:
            self.session.rollback()
            if llc("debug"):
                logging.debug("rolled back pending transaction from session")
            if raise_if_exists:
                raise exceptions.AlreadyExistsException(exc)
            for obj in objs:
                self.add(obj)
        return None

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
        return self._query(cursor_result="count", model=model, **kwargs)  # type: ignore

    def get(
        self,
        attr: str | InstrumentedAttribute[Any],
        value: str | int | float | Enum | UUID,
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

        if isinstance(attr, InstrumentedAttribute):
            attr = attr.key
        return self._query(
            cursor_result=cursor_result,
            filter_by={attr: value},
            model=model,
            **kwargs,  # type: ignore
        )

    def get_all(
        self,
        attr: str | InstrumentedAttribute[Any],
        value: str | int | float | Enum | UUID,
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
        objs = self.get(
            attr=attr,
            value=value,
            cursor_result=cursor_result,
            model=model,
            **kwargs,
        )
        return objs  # type: ignore

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
        return self.get(
            attr=attr,
            value=value,
            cursor_result=cursor_result,
            model=model,
            **kwargs,
        )

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
        return self.get(
            attr=attr,
            value=value,
            cursor_result=cursor_result,
            model=model,
            **kwargs,
        )

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
        return self.get(
            attr=attr,
            value=value,
            cursor_result=cursor_result,
            model=model,
            **kwargs,
        )

    def patch(
        self, obj: BaseDomainModel, patches: JsonPatch
    ) -> BaseDomainModel:
        """Patch a domain model object using a JSON patch document.

        Parameters
        ----------
        obj
            Patchable object to be patched.
        patches
            JSON patch document containing the changes to apply.

        Returns
        -------
        DomainModel
            Patched object.
        """
        if not hasattr(obj, "patch"):
            raise TypeError("Object does not support patch operation")
        patched = obj.patch(patches)  # type: ignore[attr-defined]
        self.session.flush()
        return cast(BaseDomainModel, patched)

    def remove(self, obj: DomainModel) -> None:
        """_summary_

        Parameters
        ----------
        obj : DomainModel
            _description_
        """
        self.session.delete(obj)
        self.session.flush()

    def remove_all(
        self,
        objs: list[DomainModel] | None = None,
        **kwargs: Any,
    ) -> None:
        """_summary_

        Parameters
        ----------
        objs : list[DomainModel] | None, optional
            _description_, by default None
        """
        if not objs:
            objs = self.select(**kwargs)  # type: ignore
        for obj in objs:
            self.remove(obj)

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
        return self._query(cursor_result=cursor_result, model=model, **kwargs)  # type: ignore

    def update(self, obj: Updateable, new: DomainModel) -> DomainModel:
        """_summary_

        Parameters
        ----------
        obj : DomainModel
            _description_
        new : DomainModel
            _description_

        Returns
        -------
        DomainModel
            _description_
        """
        obj = obj.update(new)
        self.session.flush()
        self.session.refresh(obj)
        return obj

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
        return self._query(cursor_result=cursor_result, model=model, **kwargs)  # type: ignore

    def _query(
        self,
        cursor_result: str | None = None,
        model: DomainModel | None = None,
        filters: Iterable[SearchFilter | FilterOperator] | None = None,
        query: Query[Any] | None = None,
        order_by: list[
            InstrumentedAttribute[Any]
            | UnaryExpression[Any]
            | OrderBy
            | QueryClause
        ] = list(),
        **kwargs: Any,
    ) -> Any:
        """_summary_

        Parameters
        ----------
        cursor_result : str | None, optional
            _description_, by default None
        model : DomainModel | None, optional
            _description_, by default None
        filters : list[SearchFilter  |  QueryClause | FilterOperator], optional
            _description_, by default list()
        query : Query[Any] | None, optional
            _description_, by default None
        order_by : list[ InstrumentedAttribute[Any]  |  UnaryExpression[Any]  |  OrderBy  |  QueryClause ], optional
            _description_, by default list()

        Returns
        -------
        Any
            _description_
        """
        """
        cursor_result:
            all
            first
            one
            one_or_none
            count
            None

        **kwargs:
            limit=n
            order_by=User.id
            order_by=[User.username, User.birthday]
            distinct=User.username

        """
        if not model:
            model = self._default_model

        subquery: Query[Any]

        if query:
            subquery = query
        else:
            subquery = self.session.query(model)  # type: ignore

        normalized_filters = list(filters) if filters else []
        if normalized_filters:
            filter_statements = self._process_filters(
                filters=normalized_filters, model=model
            )
            subquery = subquery.filter(*filter_statements)  # type: ignore

        for k, value in kwargs.items():
            if not value:
                break

            if isinstance(value, QueryClause):
                subquery = self._query_clause(
                    clause=value, query=subquery, model=model  # type: ignore
                )
            elif isinstance(value, dict):  # type: ignore
                subquery = getattr(subquery, k)(**value)  # type: ignore
            elif isinstance(value, list):
                for item in value:  # type: ignore
                    if isinstance(item, QueryClause):
                        subquery = self._query_clause(
                            clause=item, query=subquery, model=model  # type: ignore
                        )
                    else:
                        subquery = getattr(subquery, k)(item)  # type: ignore
            else:
                subquery = getattr(subquery, k)(value)  # type: ignore

        for order in order_by:
            if isinstance(order, QueryClause):
                subquery = self._query_clause(
                    clause=order, query=subquery, model=model  # type: ignore
                )
            elif isinstance(
                order, InstrumentedAttribute | UnaryExpression
            ):  # type: ignore
                subquery = getattr(subquery, "order_by")(order)  # type: ignore

        # Process cursor_result parameter
        if cursor_result:
            return getattr(subquery, cursor_result)()  # type: ignore

        return subquery  # type: ignore

    def _query_clause(
        self,
        clause: QueryClause,
        query: Query[Any],
        model: DomainModel,
    ) -> Query[Any]:
        if not clause._domain_model:  # type: ignore
            clause.set_domain_model(model)
        return clause.query_clause(query)

    def _process_filters(
        self,
        filters: Iterable[SearchFilter | FilterOperator],
        model: BaseDomainModel,
    ) -> list[ColumnElement[Any] | BinaryExpression[Any] | ColumnOperators]:
        """Process query filters and apply them to the query object

        Parameters
        ----------
        filters
            Filters which can be SearchFilter or FilerOperator objects
        model
            The domain model which will be used to set the `_domain_model`
            attribute of SearchFilter objects

        Returns
        -------
            Query object to which the filters have been applied
        """
        filter_expressions = [
            self._process_filter_item(filter_=f, model=model) for f in filters
        ]
        return filter_expressions

    def _process_filter_item(
        self,
        filter_: SearchFilter | FilterOperator,
        model: BaseDomainModel,
    ) -> ColumnElement[Any] | BinaryExpression[Any] | ColumnOperators:
        """Process a filter item. When the item is a SeachFilter object
        the domain model will be set and the filter statement will be returned.
        When the item is a FilterOperator object, all the filters will be
        processed recursively by this method and they are supplied to the
        filter operator.

        Parameters
        ----------
        filter_
            A filter object
        model
            Domain model type

        Returns
        -------
            Returns a filter statement or a filter operator containing
            filter statements

        Raises
        ------
        TypeError
            When an unsupported filter type is being used
        """
        if isinstance(filter_, FilterOperator):
            filters = [
                self._process_filter_item(filter_=filter_item, model=model)
                for filter_item in filter_.search_filters
            ]
            return filter_.filter_operator(*filters)  # type: ignore
        elif isinstance(filter_, SearchFilter):  # type: ignore
            if not filter_._domain_model:  # type: ignore
                filter_.set_domain_model(model)  # type: ignore
            return filter_.filter_statement
        else:
            raise TypeError(
                "Only QueryClause and FilterOperator types are allowed "
                "as values for the 'filters' argument"
            )
