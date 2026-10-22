from dataclasses import dataclass, field

from datetime import datetime
from typing import Any
from uuid import UUID

from alpha.domain.models.permission import Permission
from alpha.mixins.models.patchable import PatchableMixin
from alpha.mixins.models.updatable import UpdatableMixin
from alpha.domain.models.life_cycle_base import LifeCycleBase
from alpha.domain.models.base_model import BaseDomainModel


@dataclass(kw_only=True)
class AltTestGroup(
    LifeCycleBase, BaseDomainModel, UpdatableMixin, PatchableMixin
):
    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    permissions: list[Permission] = field(default_factory=list[Permission])

    @property
    def __patch_fields__(self) -> list[str]:
        return ["name", "description"]

    @property
    def __update_fields__(self) -> list[str]:
        return ["name", "description"]

    def to_dict(self) -> dict[str, Any]:
        permissions = [permission.to_dict() for permission in self.permissions]
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
class AltTestUser(
    LifeCycleBase, BaseDomainModel, UpdatableMixin, PatchableMixin
):
    id: UUID | None = None
    username: str
    password: str | None = None
    display_name: str | None = None
    permissions: list[Permission] = field(default_factory=list[Permission])
    groups: list[AltTestGroup] = field(default_factory=list[AltTestGroup])
    admin: bool = False
    last_login: datetime | None = None

    @property
    def __patch_fields__(self) -> list[str]:
        return [
            "username",
            "display_name",
            "admin",
        ]

    @property
    def __update_fields__(self) -> list[str]:
        return [
            "username",
            "display_name",
            "admin",
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert the User instance to a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation of the User instance.
        """
        permissions = [permission.to_dict() for permission in self.permissions]
        groups = [group.to_dict() for group in self.groups]
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
        last_login = (
            self.last_login.isoformat()
            if hasattr(self, "last_login") and self.last_login is not None
            else None
        )

        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "display_name": self.display_name,
            "permissions": permissions,
            "groups": groups,
            "admin": self.admin,
            "created_by": self.created_by
            if hasattr(self, "created_by") and self.created_by is not None
            else None,
            "created_at": created_at,
            "modified_by": self.modified_by
            if hasattr(self, "modified_by") and self.modified_by is not None
            else None,
            "modified_at": modified_at,
            "last_login": last_login,
        }
