from typing import Protocol

from alpha.domain.models.base_model import DomainModel


class Updateable(Protocol):
    def update(self, obj: DomainModel) -> DomainModel: ...
