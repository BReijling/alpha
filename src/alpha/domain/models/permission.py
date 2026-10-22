from dataclasses import dataclass
from typing import Any
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel
from alpha.domain.models.life_cycle_base import LifeCycleBase
from alpha.mixins.models.from_dict import FromDictMixin
from alpha.mixins.models.patchable import PatchableMixin
from alpha.mixins.models.updatable import UpdatableMixin


@dataclass(kw_only=True)
class Permission(
    LifeCycleBase,
    BaseDomainModel,
    UpdatableMixin,
    PatchableMixin,
    FromDictMixin,
):
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
    name: str | None = None
    description: str = ""

    @property
    def __update_fields__(self) -> list[str]:
        return ["name", "description"]

    @property
    def __patch_fields__(self) -> list[str]:
        return ["name", "description"]

    def __str__(self) -> str:
        """Return the name of the permission.

        Returns
        -------
            self.name value
        """
        return self.name or ""

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
