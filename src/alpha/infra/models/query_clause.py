from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.query import Query

from alpha import exceptions
from alpha.domain.models.base_model import BaseDomainModel


@dataclass
class QueryClause:
    field: str | InstrumentedAttribute[str]
    _domain_model: BaseDomainModel | None = None
    _instrumented_attr: InstrumentedAttribute[Any] | None = None

    def __post_init__(self) -> None:
        # Get key name if field is an instrumented attribute
        if isinstance(self.field, InstrumentedAttribute):
            self._instrumented_attr = self.field
            self.field = self.field.key

        # Try to get the instrumented attribute if only a field name is given
        self.set_domain_model()

    def query_clause(self, query: Query[Any]) -> Query[Any]:
        raise NotImplementedError

    def set_domain_model(self, model: BaseDomainModel | None = None):
        self._domain_model = model

        if not self._instrumented_attr:
            if self._domain_model:
                self._instrumented_attr = getattr(
                    self._domain_model, self.field  # type: ignore
                )

    def _raise_instrumented_attr_exception(self):
        raise exceptions.InstrumentedAttributeMissing(
            """
            The 'field' attribute needs to be of an \
sqlalchemy.orm.InstrumentedAttribute type, or specify the mapped domain model \
by adding the _domain_model attribute
            """
        )
