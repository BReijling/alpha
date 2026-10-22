from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum, auto
from typing import Any, ClassVar, Self
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import registry, relationship

from alpha.domain.models.base_model import BaseDomainModel
from alpha.domain.models.group import Group
from alpha.domain.models.life_cycle_base import LifeCycleBase
from alpha.domain.models.permission import Permission
from alpha.domain.models.user import User
from alpha.exceptions import AlreadyExistsException, NotFoundException
from alpha.mixins.models.patchable import PatchableMixin
from alpha.mixins.models.updatable import UpdatableMixin
from alpha.providers.models.token import Token


class PetType(Enum):
    DOG = auto()
    CAT = auto()
    RABBIT = auto()
    DUCK = auto()
    FOX = auto()


@dataclass
class Pet(BaseDomainModel):
    id: int = field(compare=False)
    name: str
    pet_type: PetType
    date_of_birth: date
    weight: float | None = field(compare=False, default=None)
    good_boy: bool | None = field(compare=False, default=None)
    remarks: str | None = field(compare=False, default=None)


@dataclass
class Owner(BaseDomainModel):
    id: int = field(compare=False)
    name: str
    pet: Pet


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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create an AltTestGroup instance from a dictionary.

        Parameters
        ----------
        data
            Dictionary containing group data.

        Returns
        -------
        Self
            A new AltTestGroup instance created from the dictionary.
        """
        obj = {**data}
        if "permissions" in obj:
            obj["permissions"] = [
                Permission.from_dict(permission)
                for permission in obj["permissions"]
            ]

        return cls(**obj)

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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create an AltTestUser instance from a dictionary.

        Parameters
        ----------
        data
            Dictionary containing user data.

        Returns
        -------
        Self
            A new AltTestUser instance created from the dictionary.
        """
        obj = {**data}
        if "groups" in obj:
            obj["groups"] = [
                AltTestGroup.from_dict(group) for group in obj["groups"]
            ]
        if "permissions" in obj:
            obj["permissions"] = [
                Permission(**permission) for permission in obj["permissions"]
            ]

        return cls(**obj)

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


class FakeMapper:
    started: ClassVar[bool] = False

    schema_name: ClassVar[str] = "ddd"

    mapper_registry: ClassVar = registry()

    convention: ClassVar = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    reflect_engine: ClassVar[sa.Engine | None] = None
    metadata: ClassVar = sa.MetaData(naming_convention=convention)
    if reflect_engine:
        metadata.reflect(bind=reflect_engine)

    pets = sa.Table(
        "pets",
        metadata,
        sa.Column("id", sa.INTEGER, primary_key=True, unique=True),
        sa.Column("name", sa.VARCHAR(20), primary_key=True),
        sa.Column("pet_type", sa.Enum(PetType), nullable=False),
        sa.Column("good_boy", sa.BOOLEAN, nullable=True, default=False),
        sa.Column("date_of_birth", sa.DATE, nullable=False),
        sa.Column("weight", sa.DOUBLE_PRECISION, nullable=True),
        sa.Column("remarks", sa.VARCHAR(200), nullable=True),
        sa.UniqueConstraint("name", "pet_type"),
    )

    @classmethod
    def start_mapping(cls):
        cls.mapper_registry.map_imperatively(Pet, cls.pets)

        cls.started = True


class AppMapper:
    started: ClassVar[bool] = False

    schema_name: ClassVar[str] = "public"

    mapper_registry: ClassVar = registry()

    convention: ClassVar = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    metadata: ClassVar = sa.MetaData(naming_convention=convention)

    users = sa.Table(
        "users",
        metadata,
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("username", sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column("password", sa.VARCHAR(200), nullable=True),
        sa.Column("email", sa.VARCHAR(255), nullable=True),
        sa.Column("display_name", sa.VARCHAR(255), nullable=True),
        sa.Column("role", sa.VARCHAR(50), nullable=True),
        sa.Column("permissions", sa.ARRAY(sa.VARCHAR(50)), nullable=True),
        sa.Column("groups", sa.ARRAY(sa.VARCHAR(50)), nullable=True),
        sa.Column("is_active", sa.BOOLEAN, nullable=False, default=True),
        sa.Column("admin", sa.BOOLEAN, nullable=False, default=False),
    )

    groups = sa.Table(
        "groups",
        metadata,
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column("description", sa.VARCHAR(255), nullable=True),
        sa.Column("permissions", sa.ARRAY(sa.VARCHAR(50)), nullable=True),
        sa.Column("is_active", sa.BOOLEAN, nullable=False, default=True),
    )

    refresh_tokens = sa.Table(
        "refresh_tokens",
        metadata,
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "value", sa.VARCHAR(255), nullable=False, unique=True, index=True
        ),
        sa.Column("token_type", sa.VARCHAR(10), nullable=False),
        sa.Column("subject", sa.VARCHAR(50), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Alt tables for testing alternative user and group structures
    alt_users = sa.Table(
        "alt_test_users",
        metadata,
        sa.Column(
            "id",
            sa.String,
            primary_key=True,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("username", sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column("password", sa.VARCHAR(200), nullable=True),
        sa.Column("display_name", sa.VARCHAR(255), nullable=True),
        sa.Column("admin", sa.BOOLEAN, nullable=False, default=False),
        sa.Column(
            "last_login",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("now()"),
        ),
        sa.Column("created_by", sa.String, nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_by", sa.String, nullable=True),
    )

    alt_groups = sa.Table(
        "alt_test_groups",
        metadata,
        sa.Column(
            "id",
            sa.String,
            primary_key=True,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column("description", sa.VARCHAR(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("now()"),
        ),
        sa.Column("created_by", sa.String, nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_by", sa.String, nullable=True),
    )

    alt_permissions = sa.Table(
        "alt_permissions",
        metadata,
        sa.Column(
            "id",
            sa.String,
            primary_key=True,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column("description", sa.VARCHAR(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("now()"),
        ),
        sa.Column("created_by", sa.String, nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_by", sa.String, nullable=True),
    )

    alt_user_group_couplings = sa.Table(
        "alt_test_user_group_couplings",
        metadata,
        sa.Column(
            "id",
            sa.String,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            sa.String,
            sa.ForeignKey("alt_test_users.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        ),
        sa.Column(
            "group_id",
            sa.String,
            sa.ForeignKey("alt_test_groups.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "group_id"),
    )

    alt_user_permission_couplings = sa.Table(
        "alt_test_user_permission_couplings",
        metadata,
        sa.Column(
            "id",
            sa.String,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            sa.String,
            sa.ForeignKey("alt_test_users.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        ),
        sa.Column(
            "permission_id",
            sa.String,
            sa.ForeignKey("alt_permissions.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "permission_id"),
    )

    alt_group_permission_couplings = sa.Table(
        "alt_test_group_permission_couplings",
        metadata,
        sa.Column(
            "id",
            sa.String,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "group_id",
            sa.String,
            sa.ForeignKey("alt_test_groups.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        ),
        sa.Column(
            "permission_id",
            sa.String,
            sa.ForeignKey("alt_permissions.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        ),
        sa.UniqueConstraint("group_id", "permission_id"),
    )

    @classmethod
    def start_mapping(cls):
        _map = cls.mapper_registry.map_imperatively

        _map(User, cls.users)
        _map(Group, cls.groups)
        _map(Token, cls.refresh_tokens)

        # Map alternative test group and user models for testing
        _map(
            AltTestGroup,
            cls.alt_groups,
            properties={
                "permissions": relationship(
                    Permission,
                    back_populates="groups",
                    secondary=cls.alt_group_permission_couplings,
                    lazy="selectin",
                ),
                "users": relationship(
                    AltTestUser,
                    back_populates="groups",
                    secondary=cls.alt_user_group_couplings,
                    lazy=None,
                ),
            },
        )
        _map(
            AltTestUser,
            cls.alt_users,
            properties={
                "permissions": relationship(
                    Permission,
                    back_populates="users",
                    secondary=cls.alt_user_permission_couplings,
                    lazy="selectin",
                ),
                "groups": relationship(
                    AltTestGroup,
                    back_populates="users",
                    secondary=cls.alt_user_group_couplings,
                    lazy="selectin",
                ),
            },
        )
        _map(
            Permission,
            cls.alt_permissions,
            properties={
                "users": relationship(
                    AltTestUser,
                    back_populates="permissions",
                    secondary=cls.alt_user_permission_couplings,
                    lazy=None,
                ),
                "groups": relationship(
                    AltTestGroup,
                    back_populates="permissions",
                    secondary=cls.alt_group_permission_couplings,
                    lazy=None,
                ),
            },
        )

        cls.started = True
