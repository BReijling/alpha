"""Base domain model class and type variables for domain models."""

from typing import TypeVar


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
    domain models.

    It has no attributes of its own.
    """
