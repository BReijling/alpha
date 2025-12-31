from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from sqlalchemy import BinaryExpression
from sqlalchemy.orm import Query
from sqlalchemy.orm.attributes import InstrumentedAttribute

from alpha.infra.models.query_clause import QueryClause


class Order(Enum):
    ASC = auto()
    DESC = auto()


@dataclass
class OrderBy(QueryClause):
    field: str | InstrumentedAttribute[Any] = ""
    order: Order = Order.ASC

    def __post_init__(self) -> None:
        super().__post_init__()
        self.__class__ = self._get_filter_class()

    def _get_filter_class(self):
        match self.order:
            case Order.ASC:
                return AscendingOrder
            case Order.DESC:
                return DescendingOrder


class AscendingOrder(OrderBy):
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

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.order_by(self._instrumented_attr.asc())
        self._raise_instrumented_attr_exception()


class DescendingOrder(OrderBy):
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

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.order_by(self._instrumented_attr.desc())
        self._raise_instrumented_attr_exception()
