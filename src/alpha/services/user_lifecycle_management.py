"""Contains the UserLifecycleManagement class"""

from alpha.domain.models.group import Group
from alpha.domain.models.user import User
from alpha.factories.password_factory import PasswordFactory
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.mixins.group_lifecycle import GroupLifecycleMixin
from alpha.mixins.user_lifecycle import UserLifecycleMixin


class UserLifecycleManagement(UserLifecycleMixin, GroupLifecycleMixin):
    """Management service for User CRUD transactions"""

    def __init__(
        self,
        uow: UnitOfWork,
        users_repository_name: str = "users",
        groups_repository_name: str = "groups",
        user_model: type[User] = User,
        group_model: type[Group] = Group,
        password_support: bool = False,
        password_factory: PasswordFactory | None = None,
        user_username_attribute: str = "username",
        user_password_attribute: str = "password",
    ):
        """Initializes the UserLifecycleManagement service. This service
        provides methods for managing the lifecycle of User objects, including
        creating, retrieving, updating, and deleting users. It interacts with a
        Unit of Work to manage transactions and repositories for users and
        groups. It also supports optional password hashing functionality when
        enabled.

        Parameters
        ----------
        uow
            Unit of Work instance for managing transactions
        users_repository_name
            Name of the users repository, by default "users"
        groups_repository_name
            Name of the groups repository, by default "groups"
        user_model
            User model class, by default User
        group_model
            Group model class, by default Group
        password_support
            Whether password support is enabled, by default False
        password_factory
            Factory for creating password hashes, by default None. If None, a
            default PasswordFactory will be used.
        user_username_attribute
            Attribute name for the username, by default "username"
        user_password_attribute
            Attribute name for the password, by default "password"
        """
        self.uow = uow
        self._users_repository_name = users_repository_name
        self._groups_repository_name = groups_repository_name
        self._user_model = user_model
        self._group_model = group_model
        self._password_support = password_support
        self._password_factory = password_factory or PasswordFactory()
        self._user_username_attribute = user_username_attribute
        self._user_password_attribute = user_password_attribute
