"""Contains these FilterOperator classes:
- And
- Or
"""

from typing import Any, Callable, Iterable

from sqlalchemy.orm import Query
from sqlalchemy.sql.expression import ColumnElement, and_, or_

from alpha.infra.models.search_filter import SearchFilter


class FilterOperator:
    """Base class for filter operators which can be used to specify the
    search query
    """

    def __init__(self, *search_filters: SearchFilter):
        """Instantiate the filter operator by storing the search filter
        objects
        """
        self.search_filters: Iterable[SearchFilter | FilterOperator] = (
            search_filters
        )

    @property
    def filter_operator(
        self,
    ) -> Callable[[ColumnElement[bool]], ColumnElement[bool]]:
        """Returns a filter operator

        Returns
        -------
            filter operator

        Raises
        ------
        NotImplementedError
            When called directly
        """
        raise NotImplementedError(
            "The FilterOperator class cannot be used directly. "
            "Use the And or Or classes instead."
        )

    def filter(self, query: Query[Any]) -> Query[Any]:
        """Applies the search filters on the query by using the filter operator

        Parameters
        ----------
        query
            Query object

        Returns
        -------
            Query object with filters applied
        """
        filters = [f.filter_statement for f in self.search_filters]  # type: ignore
        return query.filter(self.filter_operator(*filters))  # type: ignore


class And(FilterOperator):
    """FilterOperator which can be used to explicitly specify an 'and'
    statement to apply behaviore of SearchFilter objects which is comparable
    to AND in SQL.
    """

    @property
    def filter_operator(
        self,
    ) -> Callable[[ColumnElement[bool]], ColumnElement[bool]]:
        """Returns the 'and' filter operator

        Returns
        -------
            'and' filter operator
        """
        return and_


class Or(FilterOperator):
    """FilterOperator which can be used to explicitly specify an 'or'
    statement to apply behaviore of SearchFilter objects which is comparable
    to OR in SQL.
    """

    @property
    def filter_operator(
        self,
    ) -> Callable[[ColumnElement[bool]], ColumnElement[bool]]:
        """Returns the 'or' filter operator

        Returns
        -------
            'or' filter operator
        """
        return or_
