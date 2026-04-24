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
from alpha.interfaces.patchable import Patchable
from alpha.interfaces.updatable import Updatable
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

    Generic
    -------
        A generic type variable used to specify the domain model type for the
        repository.
    """

    def __init__(self, session: Session, default_model: DomainModel) -> None:
        """Initialize the SqlAlchemyRepository with a database session and a
        default domain model type. The session is used for all database
        interactions, and the default model is used for operations where no
        specific model type is provided.


        Parameters
        ----------
        session
            The SQLAlchemy session used for database interactions.
        default_model
            The default domain model type for the repository.
        """
        self.session = session
        self._default_model = default_model

    def add(
        self,
        obj: DomainModel,
        return_obj: bool = True,
        raise_if_exists: bool = False,
    ) -> DomainModel | None:
        """Add a domain model instance to the database session.

        Parameters
        ----------
        obj
            The domain model instance to add.
        return_obj
            Whether to return the added object, by default True
        raise_if_exists
            Whether to raise an exception if the object already exists, by
            default False

        Returns
        -------
        DomainModel | None
            The added domain model instance if return_obj is True, otherwise
            None.

        Raises
        ------
        exceptions.AlreadyExistsException
            If raise_if_exists is True and an IntegrityError occurs during the
            add operation, indicating that the object already exists in the
            database.
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
        """Add multiple domain model instances to the database session.

        Parameters
        ----------
        objs
            The list of domain model instances to add.
        return_obj
            Whether to return the added objects, by default False
        raise_if_exists
            Whether to raise an exception if any object already exists, by
            default False

        Returns
        -------
        list[DomainModel] | None
            The list of added domain model instances if return_obj is True,
            otherwise None.

        Raises
        ------
        exceptions.AlreadyExistsException
            If raise_if_exists is True and an IntegrityError occurs during the
            add operation, indicating that one or more objects already exist in
            the database.
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
        """Count the number of records in the database for a given model and
        optional filters.

        Parameters
        ----------
        model
            The domain model class to count records for, by default None

        Returns
        -------
        int
            The number of records in the database for the given model and
            filters.
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
        """Retrieve a single domain model instance from the database based on a
        specified attribute and value.

        Parameters
        ----------
        attr
            The attribute to filter by.
        value
            The value to filter by.
        cursor_result
            The type of result to return, by default "first"
        model
            The domain model class to query, by default None

        Returns
        -------
        DomainModel
            The retrieved domain model instance.
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
        """Retrieve multiple domain model instances from the database based on
        a specified attribute and value.

        Parameters
        ----------
        attr
            The attribute to filter by.
        value
            The value to filter by.
        cursor_result
            The type of result to return, by default "all"
        model
            The domain model class to query, by default None

        Returns
        -------
        list[DomainModel]
            The list of retrieved domain model instances.
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
        """Retrieve a single domain model instance from the database based on a
        specified attribute and value, expecting exactly one result.

        Parameters
        ----------
        attr
            The attribute to filter by.
        value
            The value to filter by.
        cursor_result
            The type of result to return, by default "one"
        model
            The domain model class to query, by default None

        Returns
        -------
        DomainModel
            The retrieved domain model instance.
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
        """Retrieve a single domain model instance from the database based on a
        specified attribute and value, expecting zero or one result.

        Parameters
        ----------
        attr
            The attribute to filter by.
        value
            The value to filter by.
        cursor_result
            The type of result to return, by default "one_or_none"
        model
            The domain model class to query, by default None

        Returns
        -------
        DomainModel | None
            The retrieved domain model instance or None if not found.
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
        """Retrieve a single domain model instance from the database based on
        its ID.

        Parameters
        ----------
        value
            The ID value to filter by.
        attr
            The attribute to filter by, by default "id"
        cursor_result
            The type of result to return, by default "one_or_none"
        model
            The domain model class to query, by default None

        Returns
        -------
        DomainModel | None
            The retrieved domain model instance or None if not found.
        """
        return self.get(
            attr=attr,
            value=value,
            cursor_result=cursor_result,
            model=model,
            **kwargs,
        )

    def patch(
        self, obj: Patchable[Any], patches: JsonPatch
    ) -> BaseDomainModel:
        """Patch a domain model object using a JSON patch object.

        Parameters
        ----------
        obj
            Patchable object to be patched.
        patches
            JSON patch object containing the changes to apply.

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
        """Remove a domain model instance from the database.

        Parameters
        ----------
        obj
            The domain model instance to remove.
        """
        self.session.delete(obj)
        self.session.flush()

    def remove_all(
        self,
        objs: list[DomainModel] | None = None,
        **kwargs: Any,
    ) -> None:
        """Remove multiple domain model instances from the database.

        Parameters
        ----------
        objs
            The list of domain model instances to remove, by default None
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
            The list of retrieved domain model instances.
        """
        return self._query(cursor_result=cursor_result, model=model, **kwargs)  # type: ignore

    def update(self, obj: Updatable, new: DomainModel) -> DomainModel:
        """Update a domain model instance with new data.

        Parameters
        ----------
        obj
            The domain model instance to update.
        new
            The new data to update the domain model instance with.

        Returns
        -------
        DomainModel
            The updated domain model instance.
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
            The list of retrieved domain model instances.
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
        """Select domain model instances from the database based on optional
        filters.

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

        Parameters
        ----------
        cursor_result
            The type of result to return, by default None
        model
            The domain model class to query, by default None
        filters
            The list of filters to apply, by default list()
        query
            The query object to use, by default None
        order_by
            The list of order by clauses, by default list()

        Returns
        -------
        Any
            The result of the query.
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
                    clause=value,
                    query=subquery,
                    model=model,  # type: ignore
                )
            elif isinstance(value, dict):  # type: ignore
                subquery = getattr(subquery, k)(**value)  # type: ignore
            elif isinstance(value, list):
                for item in value:  # type: ignore
                    if isinstance(item, QueryClause):
                        subquery = self._query_clause(
                            clause=item,
                            query=subquery,
                            model=model,  # type: ignore
                        )
                    else:
                        subquery = getattr(subquery, k)(item)  # type: ignore
            else:
                subquery = getattr(subquery, k)(value)  # type: ignore

        for order in order_by:
            if isinstance(order, QueryClause):
                subquery = self._query_clause(
                    clause=order,
                    query=subquery,
                    model=model,  # type: ignore
                )
            elif isinstance(order, InstrumentedAttribute | UnaryExpression):  # type: ignore
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
        """Apply a QueryClause to a query object.

        Parameters
        ----------
        clause
            The QueryClause to apply.
        query
            The query object to apply the clause to.
        model
            The domain model class to query, used to set the `_domain_model`
            attribute of the QueryClause if it is not already set.

        Returns
        -------
        Query[Any]
            The query object with the QueryClause applied.
        """
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
