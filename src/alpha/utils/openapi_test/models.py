from datetime import datetime, timedelta, timezone, date
from typing import Any, Literal, Self, Optional, Type, TypeVar
from uuid import UUID
from dataclasses import dataclass, field
from attrs import define
from pydantic import BaseModel
from enum import Enum, auto

from alpha.domain.models.base_model import BaseDomainModel
from alpha.domain.models.permission import Permission
from alpha.exceptions import AlreadyExistsException, NotFoundException
from alpha.mixins.models.from_dict import FromDictMixin
from alpha.mixins.models.patchable import PatchableMixin
from alpha.mixins.models.updatable import UpdatableMixin
from alpha.providers.models.identity import Identity
from alpha.utils.secret_generator import generate_secret


@dataclass
class LifeCycleBase:
    created_by: str | None = None
    created_at: datetime | None = None
    modified_by: str | None = None
    modified_at: datetime | None = None


@dataclass(kw_only=True)
class TestGroup(LifeCycleBase, BaseDomainModel, UpdatableMixin, FromDictMixin):
    id: UUID | int | str | None = None
    name: str | None = None
    description: str | None = None
    permissions: list[str] | None = None
    is_active: bool = True

    @property
    def __update_fields__(self) -> list[str]:
        return [
            "name",
            "description",
            "permissions",
            "is_active",
        ]


@dataclass(kw_only=True)
class TestUser(LifeCycleBase, BaseDomainModel, UpdatableMixin, FromDictMixin):
    id: UUID | int | str | None = None
    username: str | None = None
    password: str | None = None
    role: str | None = None
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    permissions: list[str] | None = None
    groups: list[TestGroup] = field(default_factory=list[TestGroup])
    is_active: bool = True
    admin: bool = False

    @property
    def __update_fields__(self) -> list[str]:
        return [
            "username",
            "display_name",
            "permissions",
            "groups",
            "admin",
        ]

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
            admin=identity.admin,
        )

    def update_from_identity(self, identity: Identity) -> None:
        return None


@dataclass
class TestToken(BaseDomainModel):
    value: str
    token_type: Literal["Bearer", "Refresh"] = "Bearer"
    subject: str | None = None
    id: UUID | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TestToken":
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

    @classmethod
    def create_refresh(
        cls,
        subject: str,
        max_age_seconds: int = 7 * 24 * 3600,
        token_length: int = 32,
    ) -> "TestToken":
        return cls(
            value=generate_secret(token_length),
            token_type="Refresh",
            subject=subject,
            created_at=datetime.now(tz=timezone.utc),
            expires_at=datetime.now(tz=timezone.utc)
            + timedelta(seconds=max_age_seconds),
        )

    def to_dict(self) -> dict[str, str | None]:
        obj: dict[str, str | None] = {
            "value": self.value,
            "subject": self.subject,
            "token_type": self.token_type,
        }

        if self.id:
            obj["id"] = str(self.id)
        if self.created_at:
            obj["created_at"] = self.created_at.isoformat()
        if self.expires_at:
            obj["expires_at"] = self.expires_at.isoformat()

        return obj


P = TypeVar("P", bound="Pet")


class PetType(Enum):
    NONE = 0
    DOG = auto()
    CAT = auto()
    RABBIT = auto()


@dataclass
class Pet:
    name: str
    pet_type: PetType
    date_of_birth: date
    weight: Optional[float] = None
    good_boy: Optional[bool] = None
    id: int = field(default=1)

    @property
    def age(self) -> int:
        delta = date(2022, 2, 2) - self.date_of_birth
        return delta.days // 365

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": 1,
            "name": self.name,
            "pet_type": self.pet_type.name,
            "age": self.age,
            "weight": self.weight,
            "good_boy": self.good_boy,
        }

    @classmethod
    def factory(cls: Type[P], **kwargs) -> P:
        return cls(
            name=kwargs["name"],
            pet_type=PetType[kwargs["pet_type"]],
            date_of_birth=kwargs["date_of_birth"],
            good_boy=kwargs["good_boy"],
        )


@define
class AttrsPet:
    name: str
    pet_type: PetType
    date_of_birth: date
    weight: Optional[float] = None
    good_boy: Optional[bool] = None
    id: int = 1


class PydanticPet(BaseModel):
    name: str
    pet_type: PetType
    date_of_birth: date
    weight: Optional[float] = None
    good_boy: Optional[bool] = None
    id: int = 1


# Models for alternative test entities
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

    def add_permission(self, permission: str | Permission) -> None:
        if permission not in self.permissions:
            self.permissions.append(permission)
        else:
            raise AlreadyExistsException(
                f"Permission '{permission}' is already added to the user."
            )

    def remove_permission(self, permission: str | Permission) -> None:
        if permission in self.permissions:
            self.permissions.remove(permission)
        else:
            raise NotFoundException(
                f"Permission '{permission}' is not associated with the user."
            )

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

    def add_group(self, group: str | AltTestGroup) -> None:
        if group not in self.groups:
            self.groups.append(group)
        else:
            raise AlreadyExistsException(
                f"Group '{group}' is already added to the user."
            )

    def add_permission(self, permission: str | Permission) -> None:
        if permission not in self.permissions:
            self.permissions.append(permission)
        else:
            raise AlreadyExistsException(
                f"Permission '{permission}' is already added to the user."
            )

    def remove_group(self, group: str | AltTestGroup) -> None:
        if group in self.groups:
            self.groups.remove(group)
        else:
            raise NotFoundException(
                f"Group '{group}' is not associated with the user."
            )

    def remove_permission(self, permission: str | Permission) -> None:
        if permission in self.permissions:
            self.permissions.remove(permission)
        else:
            raise NotFoundException(
                f"Permission '{permission}' is not associated with the user."
            )

    def to_dict(self) -> dict[str, Any]:
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
