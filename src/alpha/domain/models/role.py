from enum import Enum, auto
from typing import Self


class Role(Enum):
    """Defines user roles with varying levels of permissions. The roles are
    ordered from highest to lowest permissions. The comparison methods allow
    for easy comparison of roles based on their hierarchy. The roles are
    ordered on a scale from highest to lowest permissions.

    Permissions are not automatically assigned to roles but it gives a general
    idea of the typical permissions associated with each role. Using role-based
    access control gives you a flexible and scalable way to manage user
    permissions in your application. Using permissions, instead of roles, gives
    you more fine-grained control over user access, but can be more complex to
    manage. The choice between using roles or permissions depends on the
    specific needs of your application and the level of granularity you require
    in managing user access.

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
