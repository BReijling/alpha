from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Self, Sequence
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel
from alpha.providers.models.identity import Identity


@dataclass
class LifeCycleBase:
    created_by: str | None = None
    created_at: datetime | None = None
    modified_by: str | None = None
    modified_at: datetime | None = None


@dataclass(kw_only=True)
class TestGroup(LifeCycleBase, BaseDomainModel):
    id: UUID | int | str | None = None
    name: str | None = None
    description: str | None = None
    permissions: Sequence[str] | None = None
    is_active: bool = True


@dataclass(kw_only=True)
class TestUser(LifeCycleBase, BaseDomainModel):
    id: UUID | int | str | None = None
    username: str | None = None
    password: str | None = None
    role: str | None = None
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    permissions: Sequence[str] | None = None
    groups: Sequence[str | TestGroup] | None = None
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


@dataclass
class TestToken(BaseDomainModel):
    value: str
    token_type: Literal["Bearer", "Refresh"] = "Bearer"
    subject: str | None = None
    id: UUID | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "id": str(self.id) if self.id else None,
            "value": self.value,
            "subject": self.subject,
            "token_type": self.token_type,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "expires_at": (
                self.expires_at.isoformat() if self.expires_at else None
            ),
        }
