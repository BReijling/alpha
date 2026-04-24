from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from sqlalchemy import BinaryExpression
from sqlalchemy.orm import Query
from sqlalchemy.orm.attributes import InstrumentedAttribute

from alpha.infra.models.query_clause import QueryClause


class Order(Enum):
    """An enumeration of possible orderings for query results."""

    ASC = auto()
    DESC = auto()


@dataclass
class OrderBy(QueryClause):
    """A class representing an order by clause for SQLAlchemy queries. This
    class extends the `QueryClause` class and adds an `order` attribute
    to specify the ordering direction (ascending or descending). The `field`
    attribute can be either a string representing the field name or an
    `InstrumentedAttribute` from SQLAlchemy.
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
        """
        if self._instrumented_attr:
            return query.order_by(self._instrumented_attr.desc())
        self._raise_instrumented_attr_exception()
