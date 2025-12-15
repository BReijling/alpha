from dataclasses import dataclass
from typing import Any, TypeVar

DomainModel = TypeVar("DomainModel", bound="BaseDomainModel")
DomainModelCovariant = TypeVar(
    "DomainModelCovariant", bound="BaseDomainModel", covariant=True
)
DomainModelContravariant = TypeVar(
    "DomainModelContravariant", bound="BaseDomainModel", contravariant=True
)


@dataclass
class BaseDomainModel:
    def to_dict(self) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        for attr in self.__dataclass_fields__.keys():
            if not attr.startswith("_"):
                obj[attr] = getattr(self, attr)
            if attr == "_id":
                obj[attr] = str(getattr(self, attr))
        return obj

    def update(self, obj: DomainModel) -> DomainModel:
        raise NotImplementedError("Subclasses must implement the update method")
