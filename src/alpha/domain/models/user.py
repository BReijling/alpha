from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Self, Sequence, cast
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel, DomainModel
from alpha.domain.models.group import Group
from alpha.domain.models.life_cycle_base import LifeCycleBase

from alpha.providers.models.identity import Identity


class Role(Enum):
    """Defines user roles with varying levels of permissions. The roles are
    ordered from highest to lowest permissions. The comparison methods allow
    for easy comparison of roles based on their hierarchy. The roles are
    ordered on a scale from highest to lowest permissions.

    Typical permissions are as follows:
    - CREATE: Permission to create new content or data, but not modify existing
    content.
    - READ: Permission to read content or data.
    - UPDATE: Permission to modify existing content or data, but not create new
    content.
    - DELETE: Permission to delete content or data.
    - MANAGE_USERS: Permission to manage user accounts and permissions.
    - MANAGE_SETTINGS: Permission to manage system settings and configurations.
    - ALL: Permission to perform all actions, including user management and
    system settings.

    Roles:
    - ADMIN: Role with permissions to manage users, content, and system
    settings. Typically has the ALL permissions.
    - SUPERUSER: Role with all permissions, including system settings and user
    management. Typically has the ALL permissions, but may be used to denote a
    special type of admin user with additional privileges or responsibilities.
    - OWNER: Role with permissions to manage their own resources and users, but
    not system settings. Typically has permissions similar to ADMIN, but
    limited to their own scope of resources.
    - MODERATOR: Role with permissions to manage content and users, but not
    system settings. Typically has permissions to UPDATE and DELETE content,
    and MANAGE_USERS, but not MANAGE_SETTINGS.
    - EDITOR: Role with permissions to create and edit content, but not manage
    users or settings. Typically has permissions to CREATE, READ, UPDATE, and
    DELETE content, but not MANAGE_USERS or MANAGE_SETTINGS.
    - USER: Default role with standard permissions. Typically has permissions
    to CREATE, READ, and UPDATE their own content, but not DELETE content or
    manage users or settings.
    - VIEWER: Typical read-only role with limited permissions. Typically has
    permission to READ content, but not CREATE, UPDATE, DELETE, or manage users
    or settings.
    """

    ADMIN = auto()
    SUPERUSER = auto()
    OWNER = auto()
    MODERATOR = auto()
    EDITOR = auto()
    USER = auto()
    VIEWER = auto()

    def __lt__(self, obj: Self) -> bool:
        return self.value < obj.value

    def __le__(self, obj: Self) -> bool:
        return self.value <= obj.value

    def __gt__(self, obj: Self) -> bool:
        return self.value > obj.value

    def __ge__(self, obj: Self) -> bool:
        return self.value >= obj.value


@dataclass(kw_only=True)
class User(LifeCycleBase, BaseDomainModel):
    id: UUID | int | str | None = None
    username: str | None = None
    password: str | None = None
    role: str | Role | None = None
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    permissions: Sequence[str] | None = None
    groups: Sequence[str | Group] | None = None
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
        if not isinstance(obj, User):
            raise TypeError("User.update expects a User instance.")

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
