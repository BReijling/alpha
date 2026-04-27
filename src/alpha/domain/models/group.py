from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence, cast
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
    permissions: Sequence[str] | None = None
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert the Group instance to a dictionary.

        Returns
        -------
        dict[str, Any]
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
