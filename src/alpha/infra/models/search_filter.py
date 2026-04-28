from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import BinaryExpression, ColumnOperators

from alpha.infra.models.query_clause import QueryClause


class Operator(Enum):
    """An enumeration of possible operators for search filters.

    Can be used for the `op` attribute of the `SearchFilter` class to specify
    the operator for the filter.

    Attributes
    ----------
    LT
        Represents the "less than" operator.
    LTE
        Represents the "less than or equal to" operator.
    EQ
        Represents the "equal to" operator.
    NEQ
        Represents the "not equal to" operator.
    GT
        Represents the "greater than" operator.
    GTE
        Represents the "greater than or equal to" operator.
    IN
        Represents the "in" operator for checking if a value is in a list.
    NIN
        Represents the "not in" operator for checking if a value is not in a
        list.
    LIKE
        Represents the "like" operator for pattern matching.
    NLIKE
        Represents the "not like" operator for pattern matching.
    ILIKE
        Represents the "case-insensitive like" operator for pattern matching.
    NILIKE
        Represents the "case-insensitive not like" operator for pattern
        matching.
    STARTSWITH
        Represents the "starts with" operator for pattern matching.
    ISTARTSWITH
        Represents the "case-insensitive starts with" operator for pattern
        matching.
    NSTARTSWITH
        Represents the "not starts with" operator for pattern matching.
    NISTARTSWITH
        Represents the "case-insensitive not starts with" operator for pattern
        matching.
    ENDSWITH
        Represents the "ends with" operator for pattern matching.
    IENDSWITH
        Represents the "case-insensitive ends with" operator for pattern
        matching.
    NENDSWITH
        Represents the "not ends with" operator for pattern matching.
    NIENDSWITH
        Represents the "case-insensitive not ends with" operator for pattern
        matching.
    CONTAINS
        Represents the "contains" operator for pattern matching.
    ICONTAINS
        Represents the "case-insensitive contains" operator for pattern
        matching.
    NCONTAINS
        Represents the "not contains" operator for pattern matching.
    NICONTAINS
        Represents the "case-insensitive not contains" operator for pattern
        matching.
    """

    LT = auto()
    LTE = auto()
    EQ = auto()
    NEQ = auto()
    GT = auto()
    GTE = auto()
    IN = auto()
    NIN = auto()
    LIKE = auto()
    NLIKE = auto()
    ILIKE = auto()
    NILIKE = auto()
    STARTSWITH = auto()
    ISTARTSWITH = auto()
    NSTARTSWITH = auto()
    NISTARTSWITH = auto()
    ENDSWITH = auto()
    IENDSWITH = auto()
    NENDSWITH = auto()
    NIENDSWITH = auto()
    CONTAINS = auto()
    ICONTAINS = auto()
    NCONTAINS = auto()
    NICONTAINS = auto()


@dataclass
class SearchFilter(QueryClause):
    """A class representing a search filter for SQLAlchemy queries. This class
    extends the `QueryClause` class and adds attributes for the operator,
    field, and value of the filter.

    An instance of this class represents a single filter condition that can be
    applied to a call to the `filters` parameter of any method of a
    `SqlRepository` subclass. Keep in mind that this `filters` parameter is
    expected to be a sequence of `SearchFilter` instances, so multiple filters
    can be applied to a query by including multiple instances of this class in
    the sequence.

    Use a FilterOperator class to define AND or OR combinations of multiple
    SearchFilter instances for more complex filtering logic.

    Attributes
    ----------
    op
        An instance of the `Operator` enum specifying the type of comparison to
        be performed.
    field
        A string representing the name of the field to filter on, or an
        `InstrumentedAttribute` from SQLAlchemy representing the field.
    value
        The value to compare the field against in the filter.
    """

    op: Operator = Operator.EQ
    field: str | InstrumentedAttribute[Any] = ""
    value: Any = ""

    def __post_init__(self) -> None:
        """Post-initialization method to set up the search filter. This method
        calls the parent class's post-initialization method and then determines
        the appropriate subclass based on the operator attribute.
        """
        super().__post_init__()
        self.__class__ = self._get_filter_class()  # type: ignore

    @property
    def filter_statement(
        self,
    ) -> BinaryExpression[Any] | ColumnOperators:
        """Returns the filter statement

        Returns
        -------
        BinaryExpression | ColumnOperators
            Filter statement

        Raises
        ------
        NotImplementedError
            When called directly
        """
        raise NotImplementedError

    def _get_filter_class(self) -> type["SearchFilter"]:
        match self.op:
            case Operator.LT:
                return LessThanFilter
            case Operator.LTE:
                return LessThanEqualsFilter
            case Operator.EQ:
                return EqualsFilter
            case Operator.NEQ:
                return NotEqualsFilter
            case Operator.GT:
                return GreaterThanFilter
            case Operator.GTE:
                return GreaterThanEqualsFilter
            case Operator.IN:
                return InFilter
            case Operator.NIN:
                return NotInFilter
            case Operator.LIKE:
                return LikeFilter
            case Operator.NLIKE:
                return NotLikeFilter
            case Operator.ILIKE:
                return InsensitiveLikeFilter
            case Operator.NILIKE:
                return InsensitiveNotLikeFilter
            case Operator.STARTSWITH:
                return StartsWithFilter
            case Operator.NSTARTSWITH:
                return NotStartsWithFilter
            case Operator.ISTARTSWITH:
                return InsensitiveStartsWithFilter
            case Operator.NISTARTSWITH:
                return InsensitiveNotStartsWithFilter
            case Operator.ENDSWITH:
                return EndsWithFilter
            case Operator.NENDSWITH:
                return NotEndsWithFilter
            case Operator.IENDSWITH:
                return InsensitiveEndsWithFilter
            case Operator.NIENDSWITH:
                return InsensitiveNotEndsWithFilter
            case Operator.CONTAINS:
                return ContainsFilter
            case Operator.NCONTAINS:
                return NotContainsFilter
            case Operator.ICONTAINS:
                return InsensitiveContainsFilter
            case Operator.NICONTAINS:
                return InsensitiveNotContainsFilter

    def _parse_list(self, obj: str | list[str] | Any) -> list[str]:
        if isinstance(obj, list):
            return obj  # type: ignore
        if isinstance(obj, str):
            return obj.split(",")
        return [obj]


class LessThanFilter(SearchFilter):
    @property
    def filter_statement(self) -> BinaryExpression[Any]:
        """Returns a lesser then filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr < self.value
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr < self.value)
        self._raise_instrumented_attr_exception()


class LessThanEqualsFilter(SearchFilter):
    @property
    def filter_statement(self) -> BinaryExpression[Any]:
        """Returns a lesser then or equals filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr <= self.value
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr <= self.value)
        self._raise_instrumented_attr_exception()


class EqualsFilter(SearchFilter):
    @property
    def filter_statement(self) -> BinaryExpression[Any]:
        """Returns an equals filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr == self.value
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr == self.value)
        return query.filter_by(**{self.field: self.value})


class NotEqualsFilter(SearchFilter):
    @property
    def filter_statement(self) -> BinaryExpression[Any]:
        """Returns a not equals filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr != self.value
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr != self.value)
        self._raise_instrumented_attr_exception()


class GreaterThanFilter(SearchFilter):
    @property
    def filter_statement(self) -> BinaryExpression[Any]:
        """Returns a greater then filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr > self.value
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr > self.value)
        self._raise_instrumented_attr_exception()


class GreaterThanEqualsFilter(SearchFilter):
    @property
    def filter_statement(self) -> BinaryExpression[Any]:
        """Returns a greater then or equals filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr >= self.value
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr >= self.value)
        self._raise_instrumented_attr_exception()


class InFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns an in filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            self.value = self._parse_list(self.value)
            return self._instrumented_attr.in_(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr.in_(self.value))
        self._raise_instrumented_attr_exception()


class NotInFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a not in filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            self.value = self._parse_list(self.value)
            return self._instrumented_attr.not_in(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr.not_in(self.value))
        self._raise_instrumented_attr_exception()


class LikeFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a like filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr.like(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr.like(self.value))
        self._raise_instrumented_attr_exception()


class InsensitiveLikeFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a case insensitive like filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr.ilike(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr.ilike(self.value))
        self._raise_instrumented_attr_exception()


class NotLikeFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a not like filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return ~self._instrumented_attr.like(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(~self._instrumented_attr.like(self.value))
        self._raise_instrumented_attr_exception()


class InsensitiveNotLikeFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a case insensitive not like filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return ~self._instrumented_attr.ilike(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(~self._instrumented_attr.ilike(self.value))
        self._raise_instrumented_attr_exception()


class StartsWithFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a starts with filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr.startswith(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr.startswith(self.value))
        self._raise_instrumented_attr_exception()


class InsensitiveStartsWithFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a case insensitive starts with filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr.istartswith(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(
                self._instrumented_attr.istartswith(self.value)
            )
        self._raise_instrumented_attr_exception()


class NotStartsWithFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a not starts with filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return ~self._instrumented_attr.startswith(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(
                ~self._instrumented_attr.startswith(self.value)
            )
        self._raise_instrumented_attr_exception()


class InsensitiveNotStartsWithFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a case insensitive not starts with filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return ~self._instrumented_attr.istartswith(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(
                ~self._instrumented_attr.istartswith(self.value)
            )
        self._raise_instrumented_attr_exception()


class EndsWithFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a ends with filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr.endswith(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr.endswith(self.value))
        self._raise_instrumented_attr_exception()


class InsensitiveEndsWithFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a case insensitive ends with filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr.iendswith(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr.iendswith(self.value))
        self._raise_instrumented_attr_exception()


class NotEndsWithFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a not ends with filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return ~self._instrumented_attr.endswith(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(~self._instrumented_attr.endswith(self.value))
        self._raise_instrumented_attr_exception()


class InsensitiveNotEndsWithFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a case insensitive not ends with filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return ~self._instrumented_attr.iendswith(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(~self._instrumented_attr.iendswith(self.value))
        self._raise_instrumented_attr_exception()


class ContainsFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a contains filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr.contains(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr.contains(self.value))
        self._raise_instrumented_attr_exception()


class InsensitiveContainsFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a case insensitive contains filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return self._instrumented_attr.icontains(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(self._instrumented_attr.icontains(self.value))
        self._raise_instrumented_attr_exception()


class NotContainsFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a not contains filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return ~self._instrumented_attr.contains(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(~self._instrumented_attr.contains(self.value))
        self._raise_instrumented_attr_exception()


class InsensitiveNotContainsFilter(SearchFilter):
    @property
    def filter_statement(self) -> ColumnOperators:
        """Returns a case insensitive not contains filter statement

        Returns
        -------
            Filter statement
        """
        if self._instrumented_attr:
            return ~self._instrumented_attr.icontains(self.value)
        self._raise_instrumented_attr_exception()

    def query_clause(self, query: Query[Any]):
        if self._instrumented_attr:
            return query.filter(~self._instrumented_attr.icontains(self.value))
        self._raise_instrumented_attr_exception()
