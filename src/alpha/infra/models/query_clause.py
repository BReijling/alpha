from dataclasses import dataclass
from typing import Any, NoReturn

from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.query import Query

from alpha import exceptions
from alpha.domain.models.base_model import BaseDomainModel


@dataclass
class QueryClause:
    """A base class representing a query clause for SQLAlchemy queries. This
    class is used to build dynamic query clauses based on the specified field
    and domain model. The `field` attribute can be either a string representing
    the field name or an `InstrumentedAttribute` from SQLAlchemy.
    """

    field: str | InstrumentedAttribute[str]
    _domain_model: BaseDomainModel | None = None
    _instrumented_attr: InstrumentedAttribute[Any] | None = None

    def __post_init__(self) -> None:
        """Post-initialization method to set up the query clause. This method
        checks if the field is an instrumented attribute and sets the
        appropriate attributes."""
        # Get key name if field is an instrumented attribute
        if isinstance(self.field, InstrumentedAttribute):
            self._instrumented_attr = self.field
            self.field = self.field.key

        # Try to get the instrumented attribute if only a field name is given
        self.set_domain_model()

    def query_clause(self, query: Query[Any]) -> Query[Any]:
        """Apply the query clause to the given SQLAlchemy query."""
        raise NotImplementedError

    def set_domain_model(self, model: BaseDomainModel | None = None):
        """Set the domain model for the query clause. This is necessary to
        resolve the field name to an instrumented attribute if only a field
        name is provided.

        Parameters
        ----------
        model
            The domain model to use for resolving the field name, by default
            None
        """
        self._domain_model = model

        if self._instrumented_attr:
            return

        if self._domain_model:
            self._instrumented_attr = getattr(
                self._domain_model,
                self.field,  # type: ignore
            )

    def _raise_instrumented_attr_exception(self) -> NoReturn:
        """Raise an exception indicating that the instrumented attribute is
        missing."""
        raise exceptions.InstrumentedAttributeMissing(
            "The 'field' attribute needs to be of an "
            "sqlalchemy.orm.InstrumentedAttribute type, or specify the mapped "
            "domain model by adding the _domain_model attribute"
        )
