from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Self, Sequence, cast
from uuid import UUID

from alpha.domain.models.base_model import BaseDomainModel, DomainModel
from alpha.domain.models.group import Group
from alpha.domain.models.life_cycle_base import LifeCycleBase

from alpha.domain.models.role import Role
from alpha.providers.models.identity import Identity


@dataclass(kw_only=True)
class User(LifeCycleBase, BaseDomainModel):
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
        permissions.
    groups
        A list of groups that the user belongs to, which can be used for group-
        based access control. Each group can have its own set of permissions
        that apply to its members.
    is_active
        A boolean flag indicating whether the user account is active. Inactive
        users may not be able to log in or access certain features of the
        application.
    admin
        A boolean flag indicating whether the user has administrative
        privileges. This can be used to grant additional permissions or access
        to certain features of the application that are reserved for
        administrators.
    """

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
        Self
            A new User instance created from the Identity.
        """
        return cls(
            id=identity.subject,
            username=identity.username,
            email=identity.email,
            display_name=identity.display_name,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the User instance to a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation of the User instance.
        """
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
        }

    def update(self, obj: DomainModel) -> DomainModel:
        """Update the User instance with data from another User instance.

        Parameters
        ----------
        obj
            User object to update from.

        Returns
        -------
        DomainModel
            The updated instance of the User.
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
