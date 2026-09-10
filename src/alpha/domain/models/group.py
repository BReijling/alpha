from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel, DomainModel
from alpha.domain.models.life_cycle_base import LifeCycleBase


@dataclass(kw_only=True)
class Group(LifeCycleBase, BaseDomainModel):
    """Group domain model which represents a group of users with specific
    permissions. The Group model includes attributes for group identification,
    description, permissions, and lifecycle attributes for tracking creation
    and modification times.

    Attributes
    ----------
    id
        Unique identifier for the group, which can be a UUID, integer, or
        string.
    name
        The name of the group, used for identification and display purposes.
    description
        A brief description of the group and its purpose.
    permissions
        A list of specific permissions assigned to the group, which can be used
        for group-based access control. Each permission can represent a
        specific action or resource that the group has access to.
    is_active
        A boolean flag indicating whether the group is active. Inactive groups
        may not be able to be assigned to users or may not grant permissions to
        users assigned to the group.
    """

    id: UUID | int | str | None = None
    name: str | None = None
    description: str | None = None
    permissions: list[str] = field(default_factory=list)  # type: ignore
    is_active: bool = True

    def __str__(self) -> str:
        """Return the name-based representation of the Group instance."""
        return self.name or ""

    def __repr__(self) -> str:
        """Return the official string representation of the Group instance."""
        return (
            "Group("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"description={self.description!r}"
            ")"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the Group instance to a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation of the Group instance.
        """
        permissions = cast(
            list[str | dict[str, Any]],
            [
                p.to_dict() if hasattr(p, "to_dict") else p  # type: ignore
                for p in self.permissions
            ],
        )
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
            "permissions": permissions,
            "is_active": self.is_active,
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
        """Update the Group instance with data from another Group instance.

        Parameters
        ----------
        obj
            Group object to update from.

        Returns
        -------
        DomainModel
            The updated instance of the Group.

        Raises
        ------
        TypeError
            If the provided object is not a Group instance.
        """
        if not isinstance(obj, Group):
            raise TypeError("Group.update expects a Group instance.")

        self.name = obj.name
        self.description = obj.description
        self.permissions = obj.permissions
        self.modified_at = datetime.now(tz=timezone.utc)
        self.is_active = obj.is_active

        return cast(DomainModel, self)
