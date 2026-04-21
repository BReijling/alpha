from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence, cast
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel, DomainModel
from alpha.domain.models.life_cycle_base import LifeCycleBase


@dataclass(kw_only=True)
class Group(LifeCycleBase, BaseDomainModel):
    id: UUID | int | str | None = None
    name: str | None = None
    description: str | None = None
    permissions: Sequence[str] | None = None
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert the Group instance to a dictionary.

        Returns
        -------
            A dictionary representation of the Group instance.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "is_active": self.is_active,
        }

    def update(self, obj: DomainModel) -> DomainModel:
        """Update the Group instance with data from another Group instance.

        Parameters
        ----------
        obj
            Group object to update from.
        """
        if not isinstance(obj, Group):
            raise TypeError("Group.update expects a Group instance.")

        self.name = obj.name
        self.description = obj.description
        self.permissions = obj.permissions
        self.modified_at = datetime.now(tz=timezone.utc)
        self.is_active = obj.is_active

        return cast(DomainModel, self)
