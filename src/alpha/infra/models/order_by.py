from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from sqlalchemy import BinaryExpression
from sqlalchemy.orm import Query
from sqlalchemy.orm.attributes import InstrumentedAttribute

from alpha.infra.models.query_clause import QueryClause


class Order(Enum):
    """An enumeration of possible orderings for query results. This object can
    be used for the `order` attribute of the `OrderBy` class to specify whether
    the ordering should be ascending or descending.

    Attributes
    ----------
    ASC
        Represents ascending order.
    DESC
        Represents descending order.
    """

    ASC = auto()
    DESC = auto()


@dataclass
class OrderBy(QueryClause):
    """A class representing an order by clause for SQLAlchemy queries. This
    class extends the `QueryClause` class and adds an `order` attribute
    to specify the ordering direction (ascending or descending). The `field`
    attribute can be either a string representing the field name or an
    `InstrumentedAttribute` from SQLAlchemy.

    An instance of this class represents a single order by condition that can
    be applied to a call to the `order_by` parameter of any method of a
    `SqlRepository` subclass. Keep in mind that this `order_by` parameter is
    expected to be a sequence of `OrderBy` instances, so multiple order by
    conditions can be applied to a query by including multiple instances of
    this class in the sequence.

    Attributes
    ----------
    field
        Can be a string representing the field name or an
        `InstrumentedAttribute` from SQLAlchemy.
    order
        An instance of the `Order` enumeration specifying the ordering
        direction (ascending or descending).
    """

    field: str | InstrumentedAttribute[Any] = ""
    order: Order = Order.ASC

    def __post_init__(self) -> None:
        """Post-initialization method to set up the order by clause. This
        method calls the parent class's post-initialization method and then
        determines the appropriate subclass based on the order attribute.
        """
        super().__post_init__()
        self.__class__ = self._get_filter_class()

    def _get_filter_class(self) -> object:
        """Determine the appropriate subclass based on the order attribute."""
        match self.order:
            case Order.ASC:
                return AscendingOrder
            case Order.DESC:
                return DescendingOrder


class AscendingOrder(OrderBy):
    """A class representing an ascending order by clause for SQLAlchemy
    queries."""

    @property
    def filter_statement(self) -> BinaryExpression[Any]:
        """Returns a lesser then filter statement

        Returns
        -------
        BinaryExpression
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr.asc()
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]) -> Query[Any]:
        """Apply the order by clause to the given SQLAlchemy query.

        Parameters
        ----------
        query
            The SQLAlchemy query to apply the order by clause to.

        Returns
        -------
        Query
            The modified SQLAlchemy query with the order by clause applied.
        """
        if self._instrumented_attr:
            return query.order_by(self._instrumented_attr.asc())
        self._raise_instrumented_attr_exception()


class DescendingOrder(OrderBy):
    """A class representing a descending order by clause for SQLAlchemy
    queries."""

    @property
    def filter_statement(self) -> BinaryExpression[Any]:
        """Returns a lesser then filter statement

        Returns
        -------
        BinaryExpression
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr.desc()
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]) -> Query[Any]:
        """Apply the order by clause to the given SQLAlchemy query.

        Parameters
        ----------
        query
            The SQLAlchemy query to apply the order by clause to.

        Returns
        -------
        Query
            The modified SQLAlchemy query with the order by clause applied.
        """
        if self._instrumented_attr:
            return query.order_by(self._instrumented_attr.desc())
        self._raise_instrumented_attr_exception()
