"""Contains the UserLifecycleManagement class"""

from uuid import UUID

from alpha.domain.models.group import Group
from alpha.domain.models.user import User
from alpha.exceptions import BadRequestException, NotFoundException
from alpha.factories.password_factory import PasswordFactory
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.providers.models.identity import Identity


class UserLifecycleManagement:
    """Management service for User CRUD transactions"""

    def __init__(
        self,
        uow: UnitOfWork,
        users_repository_name: str = "users",
        groups_repository_name: str = "groups",
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
        users_repository_name, optional
            Name of the users repository, by default "users"
        groups_repository_name, optional
            Name of the groups repository, by default "groups"
        password_support, optional
            Whether password support is enabled, by default False
        password_factory, optional
            Factory for creating password hashes, by default None. If None, a
            default PasswordFactory will be used.
        user_username_attribute, optional
            Attribute name for the username, by default "username"
        user_password_attribute, optional
            Attribute name for the password, by default "password"
        """
        self.uow = uow
        self._users_repository_name = users_repository_name
        self._groups_repository_name = groups_repository_name
        self._password_support = password_support
        self._password_factory = password_factory or PasswordFactory()
        self._user_username_attribute = user_username_attribute
        self._user_password_attribute = user_password_attribute

    def add_user(self, user: User, identity: Identity | None = None) -> User:
        """Adds a new user object to the repository

        Parameters
        ----------
        user
            New user object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `created_by` attribute of the user will be updated
            with the username from the identity.

        Returns
        -------
            Created user object
        """
        if not hasattr(user, self._user_username_attribute) or not getattr(
            user, self._user_username_attribute
        ):
            raise BadRequestException("Username of User attribute is empty")

        if self._password_support:
            if not hasattr(user, self._user_password_attribute) or not getattr(
                user, self._user_password_attribute
            ):
                raise BadRequestException(
                    "Password of User attribute is empty"
                )

            setattr(
                user,
                self._user_password_attribute,
                self._password_factory.hash_password(
                    password=getattr(user, self._user_password_attribute)
                ),
            )

        if identity:
            user.created_by = identity.username

        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )
            user = users.add(user, raise_if_exists=True)
            self.uow.commit()
            return user

    def add_group(
        self, group: Group, identity: Identity | None = None
    ) -> Group:
        """Adds a new group object to the repository

        Parameters
        ----------
        group
            New group object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `created_by` attribute of the group will be updated
            with the username from the identity.

        Returns
        -------
            Created group object
        """
        if identity:
            group.created_by = identity.username

        with self.uow:
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )
            group = groups.add(group, raise_if_exists=True)
            self.uow.commit()
            return group

    def get_user(self, user_id: UUID) -> User:
        """Get an user object by id from the repository

        Parameters
        ----------
        user_id
            The id of the user object

        Returns
        -------
            User object which corresponds to the id

        Raises
        ------
        NotFoundException
            When the object is not found in the repository
        """
        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )
            user = users.get_by_id(user_id)

            if not user:
                raise NotFoundException(
                    f"User with id '{user_id}' is not found"
                )

            return user

    def get_group(self, group_id: UUID) -> Group:
        """Get a group object by id from the repository

        Parameters
        ----------
        group_id
            The id of the group object

        Returns
        -------
            Group object which corresponds to the id

        Raises
        ------
        NotFoundException
            When the object is not found in the repository
        """
        with self.uow:
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )
            group = groups.get_by_id(group_id)

            if not group:
                raise NotFoundException(
                    f"Group with id '{group_id}' is not found"
                )

            return group

    def get_users(self) -> list[User]:
        """Gets all user objects from the repository

        Returns
        -------
            A collection of all the user objects
        """
        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )
            result = users.select()

            return result

    def get_groups(self) -> list[Group]:
        """Gets all group objects from the repository

        Returns
        -------
            A collection of all the group objects
        """
        with self.uow:
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )
            result = groups.select()

            return result

    def remove_user(self, user_id: UUID) -> None:
        """Removes an user object from the repository

        Parameters
        ----------
        user_id
            The id of the user object
        """
        user = self.get_user(user_id=user_id)
        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )

            users.remove(user)
            self.uow.commit()

    def remove_group(self, group_id: UUID) -> None:
        """Removes a group object from the repository

        Parameters
        ----------
        group_id
            The id of the group object
        """
        group = self.get_group(group_id=group_id)
        with self.uow:
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )

            groups.remove(group)
            self.uow.commit()

    def update_user(
        self, user_id: UUID, user: User, identity: Identity | None = None
    ) -> User:
        """Updates an existing user object in the repository

        Parameters
        ----------
        user
            User object with changes
        user_id
            The id of the user object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `modified_by` attribute of the user will be updated
            with the username from the identity.

        Returns
        -------
            Updated user object
        """
        original_user = self.get_user(user_id=user_id)

        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )
            updated_user = users.update(original_user, user)
            if identity:
                updated_user.modified_by = identity.username
            self.uow.commit()

        return updated_user

    def update_group(
        self, group_id: UUID, group: Group, identity: Identity | None = None
    ) -> Group:
        """Updates an existing group object in the repository

        Parameters
        ----------
        group
            Group object with changes
        group_id
            The id of the group object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `modified_by` attribute of the group will be updated
            with the username from the identity.

        Returns
        -------
            Updated group object
        """
        original_group = self.get_group(group_id=group_id)

        with self.uow:
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )
            updated_group = groups.update(original_group, group)
            if identity:
                updated_group.modified_by = identity.username
            self.uow.commit()

        return updated_group
