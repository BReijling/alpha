from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Self, Sequence, cast
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel, DomainModel
from alpha.domain.models.life_cycle_base import LifeCycleBase

from alpha.providers.models.identity import Identity


@dataclass(kw_only=True)
class User(LifeCycleBase, BaseDomainModel):
    id: UUID | int | str | None = None
    username: str | None = None
    password: str | None = None
    role: str | None = None
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    permissions: Sequence[str] | None = None
    groups: Sequence[str] | None = None
    is_active: bool = True
    admin: bool = False

    @classmethod
    def from_identity(cls, identity: Identity) -> Self:
        """Create a User instance from an Identity instance.

        Parameters
        ----------
        identity
            Identity object to convert.

        Returns
        -------
            User instance created from the Identity.
        """
        return cls(
            id=identity.subject,
            username=identity.username,
            email=identity.email,
            display_name=identity.display_name,
        )

    def update(self, obj: DomainModel) -> DomainModel:
        """Update the User instance with data from another User instance.

        Parameters
        ----------
        user
            User object to update from.
        """
        if not isinstance(obj, User):
            raise TypeError("User.update expects a User instance.")

        self.username = obj.username
        self.email = obj.email
        self.phone = obj.phone
        self.display_name = obj.display_name
        self.permissions = obj.permissions
        self.groups = obj.groups
        self.updated_at = datetime.now(tz=timezone.utc)
        self.is_active = obj.is_active
        self.admin = obj.admin
        return cast(DomainModel, self)
