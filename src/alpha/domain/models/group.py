from dataclasses import dataclass, field
from typing import Any, cast
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel
from alpha.domain.models.life_cycle_base import LifeCycleBase
from alpha.domain.models.permission import Permission
from alpha.exceptions import AlreadyExistsException, NotFoundException
from alpha.mixins.models.from_dict import FromDictMixin
from alpha.mixins.models.patchable import PatchableMixin
from alpha.mixins.models.updatable import UpdatableMixin


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
        specific action or resource that the group has access to.
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
    permissions: list[str | Permission] = field(default_factory=list)  # type: ignore
    is_active: bool = True

    @property
    def __patch_fields__(self) -> list[str]:
        return ["name", "description", "permissions", "is_active"]

    @property
    def __update_fields__(self) -> list[str]:
        return ["name", "description", "permissions", "is_active"]

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

    def add_permission(self, permission: str | Permission) -> None:
        """Add a permission to the user's permissions list.

        Parameters
        ----------
        permission
            The permission to add.
        """
        if permission not in self.permissions:
            self.permissions.append(permission)
        else:
            raise AlreadyExistsException(
                f"Permission '{permission}' is already added to the user."
            )

    def remove_permission(self, permission: str | Permission) -> None:
        """Remove a permission from the user's permissions list.

        Parameters
        ----------
        permission
            The permission to remove.
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
        else:
            raise NotFoundException(
                f"Permission '{permission}' is not associated with the user."
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
