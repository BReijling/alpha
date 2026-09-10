from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel, DomainModel
from alpha.domain.models.life_cycle_base import LifeCycleBase


@dataclass(kw_only=True)
class Permission(LifeCycleBase, BaseDomainModel):
    """Permission class representing a system permission. This class is used to
    define and manage permissions. User and group permissions are handled
    through this class.

    Attributes
    ----------
    id
        Unique identifier for the permission. Can be a UUID, integer, or
        string.
    name
        Name of the permission.
    description
        Description for the purpose of the permission.
    """

    id: UUID | int | str | None = None
    name: str
    description: str = ""

    def __str__(self) -> str:
        """Return the name of the permission.

        Returns
        -------
            self.name value
        """
        return self.name

    def __repr__(self) -> str:
        """Return the official string representation of the object.

        Returns
        -------
            A string representing the Permission instance.
        """
        return (
            f"Permission(name={self.name!r}, description={self.description!r})"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the Permission instance to a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation of the Permission instance.
        """
        created_at = (
            self.created_at.isoformat()
            if hasattr(self, "created_at") and self.created_at is not None
            else None
        )
        modified_at = (
            self.modified_at.isoformat()
            if hasattr(self, "modified_at") and self.modified_at is not None
            else None
        )

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by
            if hasattr(self, "created_by") and self.created_by is not None
            else None,
            "created_at": created_at,
            "modified_by": self.modified_by
            if hasattr(self, "modified_by") and self.modified_by is not None
            else None,
            "modified_at": modified_at,
        }

    def update(self, obj: DomainModel) -> DomainModel:
        """Update the Permission instance with data from another Permission
        instance.

        Parameters
        ----------
        obj
            Permission object to update from.

        Returns
        -------
        DomainModel
            The updated instance of the Permission.

        Raises
        ------
        TypeError
            If the provided object is not a Permission instance.
        """
        if not isinstance(obj, Permission):
            raise TypeError("Permission.update expects a Permission instance.")

        self.name = obj.name
        self.description = obj.description
        self.modified_at = datetime.now(tz=timezone.utc)

        return cast(DomainModel, self)
