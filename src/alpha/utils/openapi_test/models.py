from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Self, Sequence, cast, Any
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel, DomainModel
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

    def update(self, obj: DomainModel) -> DomainModel:
        """Update the User instance with data from another User instance.

        Parameters
        ----------
        obj
            User object to update from.
        """
        self.username = obj.username
        self.email = obj.email
        self.phone = obj.phone
        self.display_name = obj.display_name
        self.permissions = obj.permissions
        self.groups = obj.groups
        self.modified_at = datetime.now(tz=timezone.utc)
        self.is_active = obj.is_active
        self.admin = obj.admin
        return cast(DomainModel, self)


@dataclass
class TestToken(BaseDomainModel):
    value: str
    token_type: Literal["Bearer", "Refresh"] = "Bearer"
    subject: str | None = None
    id: UUID | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Token(value='<redacted>', token_type='{self.token_type}')"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Token":
        return cls(
            id=UUID(data["id"]) if data.get("id") else None,
            value=data["value"],
            subject=data.get("subject"),
            token_type=data.get("token_type", "Bearer"),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
        )

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
