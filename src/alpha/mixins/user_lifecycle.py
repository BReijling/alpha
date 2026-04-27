"""Contains the UserLifecycleMixin class"""

from uuid import UUID

from alpha.domain.models.user import User
from alpha.exceptions import BadRequestException, NotFoundException
from alpha.factories.password_factory import PasswordFactory
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.providers.models.identity import Identity


class UserLifecycleMixin:
    """Mixin class providing methods for managing the lifecycle of User
    objects.
    """

    uow: UnitOfWork
    _users_repository_name: str
    _user_model: type[User]
    _password_support: bool
    _password_factory: PasswordFactory
    _user_username_attribute: str
    _user_password_attribute: str

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
        User
            Created user object
        """
        user = self._user_model(**user.to_dict())

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

    def get_user(self, user_id: str | int | UUID) -> User:
        """Get an user object by id from the repository

        Parameters
        ----------
        user_id
            The id of the user object

        Returns
        -------
        User
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

    def get_users(self) -> list[User]:
        """Gets all user objects from the repository

        Returns
        -------
        list[User]
            A collection of all the user objects
        """
        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )
            result = users.select()

            return result

    def remove_user(self, user_id: str | int | UUID) -> None:
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

    def update_user(
        self,
        user_id: str | int | UUID,
        user: User,
        identity: Identity | None = None,
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
        User
            Updated user object
        """
        user = self._user_model(**user.to_dict())

        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )
            original_user = users.get_by_id(user_id)

            if not original_user:
                raise NotFoundException(
                    f"User with id '{user_id}' is not found"
                )

            updated_user = original_user.update(user)
            if identity:
                updated_user.modified_by = identity.username
            self.uow.commit()

        return updated_user
