from dataclasses import dataclass, field
from typing import Any, Self, cast, Sequence
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel
from alpha.domain.models.life_cycle_base import LifeCycleBase
from alpha.domain.models.permission import Permission
from alpha.exceptions import AlreadyExistsException, NotFoundException
from alpha.mixins.models.from_dict import FromDictMixin
from alpha.mixins.models.patchable import PatchableMixin
from alpha.mixins.models.updatable import UpdatableMixin
from alpha.utils.parse_to_datetime import to_datetime


@dataclass(kw_only=True)
class Group(
    LifeCycleBase,
    BaseDomainModel,
    UpdatableMixin,
    PatchableMixin,
    FromDictMixin,
):
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
        specific action or resource that the group has access to. By default
        this attribute is typed as a list of strings. It can be modified to
        include other types if needed, such as `Permission` objects.
    is_active
        A boolean flag indicating whether the group is active. Inactive groups
        may not be able to be assigned to users or may not grant permissions to
        users assigned to the group.
    created_by
        The identifier of the user who created the group.
    created_at
        The timestamp when the group was created.
    modified_by
        The identifier of the user who last modified the group.
    modified_at
        The timestamp when the group was last modified.
    """

    id: UUID | int | str | None = None
    name: str | None = None
    description: str | None = None
    permissions: list[str] = field(default_factory=list[str])
    is_active: bool = True

    @property
    def __patch_fields__(self) -> Sequence[str]:
        return ("name", "description", "permissions", "is_active")

    @property
    def __update_fields__(self) -> Sequence[str]:
        return ("name", "description", "permissions", "is_active")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a Group instance from a dictionary.

        Parameters
        ----------
        data
            Dictionary containing group data.

        Returns
        -------
        Self
            A new Group instance created from the dictionary.
        """
        obj = super().from_dict(data)
        if "created_at" in data:
            obj.created_at = to_datetime(
                data["created_at"], fail_silently=False
            )
        if "modified_at" in data:
            obj.modified_at = to_datetime(
                data["modified_at"], fail_silently=False
            )

        return obj

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

    def add_permission(self, permission: str) -> None:
        """Add a permission to the group's permissions list.

        Parameters
        ----------
        permission
            The permission to add.
        """
        if permission not in self.permissions:
            self.permissions.append(permission)
        else:
            raise AlreadyExistsException(
                f"Permission '{permission}' is already added to the group."
            )

    def remove_permission(self, permission: str) -> None:
        """Remove a permission from the group's permissions list.

        Parameters
        ----------
        permission
            The permission to remove.
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
        else:
            raise NotFoundException(
                f"Permission '{permission}' is not associated with the group."
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


@dataclass(kw_only=True)
class GroupWithObjects(Group):
    """Group class with related objects included, such as permissions."""

    permissions: list[Permission] = field(default_factory=list[Permission])  # type: ignore

    @property
    def __patch_fields__(self) -> Sequence[str]:
        return ("name", "description", "is_active")

    @property
    def __update_fields__(self) -> Sequence[str]:
        return ("name", "description", "is_active")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a Group instance from a dictionary.

        Parameters
        ----------
        data
            Dictionary containing group data.

        Returns
        -------
        Self
            A new Group instance created from the dictionary.
        """
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            permissions=[
                Permission.from_dict(p) for p in data.get("permissions", [])
            ],
            is_active=data.get("is_active", True),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            modified_by=data.get("modified_by"),
            modified_at=data.get("modified_at"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the Group instance to a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation of the Group instance.
        """
        data = super().to_dict()
        data["permissions"] = [p.to_dict() for p in self.permissions]
        return data
