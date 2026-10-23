from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self, Sequence
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel
from alpha.domain.models.group import Group, GroupWithObjects
from alpha.domain.models.permission import Permission
from alpha.domain.models.life_cycle_base import LifeCycleBase
from alpha.domain.models.role import Role
from alpha.exceptions import NotFoundException, AlreadyExistsException
from alpha.mixins.models.from_dict import FromDictMixin
from alpha.mixins.models.patchable import PatchableMixin
from alpha.mixins.models.updatable import UpdatableMixin
from alpha.providers.models.identity import Identity
from alpha.utils.parse_to_datetime import to_datetime


@dataclass(kw_only=True)
class User(
    LifeCycleBase,
    BaseDomainModel,
    UpdatableMixin,
    PatchableMixin,
    FromDictMixin,
):
    """User domain model which represents a user in the system. The User model
    includes attributes for user identification, authentication, and
    authorization, as well as lifecycle attributes for tracking creation and
    modification times.

    Attributes
    ----------
    id
        Unique identifier for the user, which can be a UUID, integer, or
        string.
    username
        The username of the user, used for authentication and identification.
    password
        The password of the user, used for authentication. In a real
        application, this should be stored securely (e.g., hashed and salted).
    role
        The role of the user, which can be a string or an instance of the Role
        enum. The role determines the permissions and access level of the user.
    email
        The email address of the user, used for communication and
        identification.
    phone
        The phone number of the user, used for communication and
        identification.
    display_name
        The display name of the user, used for showing the user's name in the
        UI.
    permissions
        A list of specific permissions assigned to the user, which can be used
        for fine-grained access control. This can be used in conjunction with
        the role to provide additional permissions or override role-based
        permissions. By default this attribute is typed as a list of strings.
        It can be modified to include other types if needed, such as
        `Permission` objects.
    groups
        A list of groups that the user belongs to, which can be used for group-
        based access control. Each group can have its own set of permissions
        that apply to its members. By default this attribute is typed as a list
        of strings. It can be modified to include other types if needed, such
        as `Group` objects.
    is_active
        A boolean flag indicating whether the user account is active. Inactive
        users may not be able to log in or access certain features of the
        application.
    admin
        A boolean flag indicating whether the user has administrative
        privileges. This can be used to grant additional permissions or access
        to certain features of the application that are reserved for
        administrators.
    last_login
        The timestamp of the user's last login. This can be used to track user
        activity and for security purposes. It should be a datetime object or
        None if the user has never logged in.
    """

    id: UUID | int | str | None = None
    username: str | None = None
    password: str | None = None
    role: str | Role | None = None
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    permissions: list[str] = field(default_factory=list[str])
    groups: list[str] = field(default_factory=list[str])
    is_active: bool = True
    admin: bool = False
    last_login: datetime | None = None

    @property
    def __patch_fields__(self) -> Sequence[str]:
        return (
            "username",
            "email",
            "phone",
            "display_name",
            "permissions",
            "groups",
            "is_active",
            "admin",
        )

    @property
    def __update_fields__(self) -> Sequence[str]:
        return (
            "username",
            "email",
            "phone",
            "display_name",
            "permissions",
            "groups",
            "is_active",
            "admin",
        )

    def __str__(self) -> str:
        """Return the username of the user.

        Returns
        -------
            self.username value
        """
        return self.username or ""

    def __repr__(self) -> str:
        """Return the official string representation of the object.

        Returns
        -------
            A string representing the User instance.
        """
        return (
            "User("
            f"id={self.id}, "
            f"username={self.username!r}, "
            f"display_name={self.display_name!r}, "
            f"permissions={self.permissions!r}, "
            f"groups={self.groups!r}"
            ")"
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a User instance from a dictionary.

        Parameters
        ----------
        data
            Dictionary containing user data.

        Returns
        -------
        Self
            A new User instance created from the dictionary.
        """
        obj = super().from_dict(data)
        if "created_at" in data:
            obj.created_at = to_datetime(
                data["created_at"], fail_silently=False
            )
        if "modified_at" in data:
            obj.modified_at = to_datetime(
                data["modified_at"], fail_silently=False
            )
        if "last_login" in data:
            obj.last_login = to_datetime(
                data["last_login"], fail_silently=False
            )

        return obj

    @classmethod
    def from_identity(cls, identity: Identity) -> Self:
        """Create a User instance from an Identity instance.

        Parameters
        ----------
        identity
            Identity object to convert.

        Returns
        -------
        Self
            A new User instance created from the Identity.
        """
        return cls(
            id=identity.subject,
            username=identity.username,
            email=identity.email,
            display_name=identity.display_name,
            admin=identity.admin,
        )

    def add_group(self, group: str) -> None:
        """Add a group to the user's groups list.

        Parameters
        ----------
        group
            The group to add.
        """
        if group not in self.groups:
            self.groups.append(group)
        else:
            raise AlreadyExistsException(
                f"Group '{group}' is already added to the user."
            )

    def add_permission(self, permission: str) -> None:
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

    def remove_group(self, group: str) -> None:
        """Remove a group from the user's groups list.

        Parameters
        ----------
        group
            The group to remove.
        """
        if group in self.groups:
            self.groups.remove(group)
        else:
            raise NotFoundException(
                f"Group '{group}' is not associated with the user."
            )

    def remove_permission(self, permission: str) -> None:
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
        """Convert the User instance to a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation of the User instance.
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
        last_login = (
            self.last_login.isoformat()
            if hasattr(self, "last_login") and self.last_login is not None
            else None
        )

        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "email": self.email,
            "phone": self.phone,
            "display_name": self.display_name,
            "permissions": self.permissions,
            "groups": self.groups,
            "is_active": self.is_active,
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

    def update_from_identity(self, identity: Identity) -> Self:
        """Update the User instance with data from an Identity instance. Only
        the email and display name are updated.

        Parameters
        ----------
        identity
            Identity object to update from.
        """
        self.email = identity.email
        self.display_name = identity.display_name
        return self


@dataclass(kw_only=True)
class UserWithGroupObjects(User):
    """User class with related objects included, such as groups.

    This class extends the User class and overrides the groups attribute to
    include related Group objects.
    """

    groups: list[Group] = field(  # type: ignore
        default_factory=list[Group]
    )

    @property
    def __patch_fields__(self) -> Sequence[str]:
        return (
            "username",
            "email",
            "phone",
            "display_name",
            "permissions",
            "is_active",
            "admin",
        )

    @property
    def __update_fields__(self) -> Sequence[str]:
        return (
            "username",
            "email",
            "phone",
            "display_name",
            "permissions",
            "is_active",
            "admin",
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a User instance from a dictionary.

        Parameters
        ----------
        data
            Dictionary containing user data.

        Returns
        -------
        Self
            A new User instance created from the dictionary.
        """
        return cls(
            id=data.get("id"),
            username=data.get("username"),
            password=data.get("password"),
            email=data.get("email"),
            phone=data.get("phone"),
            display_name=data.get("display_name"),
            groups=[Group.from_dict(g) for g in data.get("groups", [])],
            is_active=data.get("is_active", True),
            admin=data.get("admin", False),
            created_by=data.get("created_by"),
            created_at=to_datetime(data["created_at"], fail_silently=False),
            modified_by=data.get("modified_by"),
            modified_at=to_datetime(data["modified_at"], fail_silently=False),
            last_login=to_datetime(data["last_login"], fail_silently=False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the User instance to a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation of the User instance.
        """
        data = super().to_dict()
        data["groups"] = [g.to_dict() for g in self.groups]
        return data


@dataclass(kw_only=True)
class UserWithObjects(User):
    """User class with related objects included, such as permissions and
    groups.

    This class extends the User class and overrides the groups and permissions
    attributes to include related Group and Permission objects. Use this class
    in combination with the GroupWithObjects class when you need to work with
    related objects.
    """

    permissions: list[Permission] = field(default_factory=list[Permission])  # type: ignore
    groups: list[GroupWithObjects] = field(  # type: ignore
        default_factory=list[GroupWithObjects]
    )

    @property
    def __patch_fields__(self) -> Sequence[str]:
        return (
            "username",
            "email",
            "phone",
            "display_name",
            "is_active",
            "admin",
        )

    @property
    def __update_fields__(self) -> Sequence[str]:
        return (
            "username",
            "email",
            "phone",
            "display_name",
            "is_active",
            "admin",
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a User instance from a dictionary.

        Parameters
        ----------
        data
            Dictionary containing user data.

        Returns
        -------
        Self
            A new User instance created from the dictionary.
        """
        return cls(
            id=data.get("id"),
            username=data.get("username"),
            password=data.get("password"),
            email=data.get("email"),
            phone=data.get("phone"),
            display_name=data.get("display_name"),
            groups=[
                GroupWithObjects.from_dict(g) for g in data.get("groups", [])
            ],
            permissions=[
                Permission.from_dict(p) for p in data.get("permissions", [])
            ],
            is_active=data.get("is_active", True),
            admin=data.get("admin", False),
            created_by=data.get("created_by"),
            created_at=to_datetime(data["created_at"], fail_silently=False),
            modified_by=data.get("modified_by"),
            modified_at=to_datetime(data["modified_at"], fail_silently=False),
            last_login=to_datetime(data["last_login"], fail_silently=False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the User instance to a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation of the User instance.
        """
        data = super().to_dict()
        data["permissions"] = [p.to_dict() for p in self.permissions]
        data["groups"] = [g.to_dict() for g in self.groups]
        return data
