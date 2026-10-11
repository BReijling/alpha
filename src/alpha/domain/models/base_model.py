"""Base domain model class and type variables for domain models."""

from typing import Any, TypeVar


DomainModel = TypeVar("DomainModel", bound="BaseDomainModel")
DomainModelCovariant = TypeVar(
    "DomainModelCovariant", bound="BaseDomainModel", covariant=True
)
DomainModelContravariant = TypeVar(
    "DomainModelContravariant", bound="BaseDomainModel", contravariant=True
)


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

        attributes: list[str] = []

        if hasattr(self, "__dataclass_fields__"):
            attributes = getattr(self, "__dataclass_fields__").keys()
        elif hasattr(self, "__attrs_attrs__"):
            attributes = [
                field.name for field in getattr(self, "__attrs_attrs__")
            ]
        elif hasattr(self, "__pydantic_fields__"):
            attributes = getattr(self, "__pydantic_fields__").keys()
        elif hasattr(self, "__slots__"):
            attributes = list(getattr(self, "__slots__"))
        else:
            attributes = list(getattr(self, "__dict__").keys())

        for attr in attributes:
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
