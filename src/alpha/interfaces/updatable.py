from typing import Protocol

from alpha.domain.models.base_model import DomainModel


class Updatable(Protocol):
    def update(self, obj: DomainModel) -> DomainModel: ...
