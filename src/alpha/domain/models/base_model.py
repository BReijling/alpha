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
    """Base class for all domain models which can be inherited by all domain
    models in the application.

    This class is mainly being used to provide a common interface for all
    domain models, and to provide a common method for converting the domain
    model instance to a dictionary.

    It has no attributes of its own.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert the domain model instance to a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation of the domain model instance.
        """
        obj: dict[str, Any] = {}
        for attr in self.__dataclass_fields__.keys():
            if not attr.startswith("_"):
                obj[attr] = getattr(self, attr)
            if attr == "_id":
                obj[attr] = str(getattr(self, attr))
        return obj

    def update(self, obj: DomainModel) -> DomainModel:
        """Update the current instance with the values from another instance.

        Parameters
        ----------
        obj
            Object to update the current instance with.

        Returns
        -------
        DomainModel
            The updated instance of the domain model.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in the subclass.
        """
        raise NotImplementedError(
            "Subclasses must implement the update method"
        )
