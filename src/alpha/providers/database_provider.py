"""Database Identity Provider implementation"""

import logging

from alpha.domain.models.user import User
from alpha.factories.password_factory import PasswordFactory
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.token_factory import TokenFactory
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.mixins.jwt_provider import JWTProviderMixin
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity
from alpha import exceptions


class DatabaseProvider(JWTProviderMixin):
    """Database Identity Provider implementation."""

    protocol = "database"
    _token_factory: TokenFactory | None = None

    def __init__(
        self,
        uow: UnitOfWork,
        token_factory: TokenFactory | None = None,
        password_factory: PasswordFactory | None = None,
        user_name_attribute: str = "username",
        users_repository_name: str = "users",
    ) -> None:
        """Database Identity Provider implementation for user authentication
        and management. This provider uses a database to store user information
        and credentials, and provides methods for authenticating users,
        retrieving user information, and changing passwords.

        Parameters
        ----------
        uow
            Unit of work instance to manage database transactions
        token_factory
            Token factory instance to generate and validate tokens
        password_factory, optional
            Password factory instance to handle password hashing and
            verification, by default None
        user_name_attribute, optional
            Attribute name to identify the user, by default "username"
        users_repository_name, optional
            Repository name for user entities, by default "users"
        """
        self.uow = uow
        self._token_factory = token_factory
        self._password_factory = password_factory or PasswordFactory()
        self._user_name_attribute = user_name_attribute
        self._users_repository_name = users_repository_name

    def authenticate(self, credentials: PasswordCredentials) -> Identity:
        """Authenticate a user using their credentials.

        Parameters
        ----------
        credentials
            Password credentials for the user

        Returns
        -------
            Identity instance representing the authenticated user
        """
        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )
            user = self._verify_password(
                credentials=credentials, user_repository=users
            )

            return Identity.from_user(user)

    def get_user(self, subject: str) -> Identity:
        """Retrieve a user by their subject identifier.

        Parameters
        ----------
        subject
            The subject identifier of the user

        Returns
        -------
            Identity instance representing the user
        """
        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )
            user = self._get_user(username=subject, user_repository=users)

            return Identity.from_user(user)

    def change_password(
        self, credentials: PasswordCredentials, new_password: str
    ) -> None:
        """Change the password for a user.

        Parameters
        ----------
        credentials
            Password credentials for the user
        new_password
            The new password to set for the user
        """
        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )
            user = self._verify_password(
                credentials=credentials, user_repository=users
            )

            self._update_user_password(
                user, new_password, user_repository=users
            )
            self.uow.commit()

    def _get_user(
        self, username: str, user_repository: SqlRepository[User]
    ) -> User:
        """Retrieve a user by their username.

        Parameters
        ----------
        username
            The username of the user
        user_repository
            The repository to query for the user

        Returns
        -------
            User instance representing the retrieved user

        Raises
        ------
        exceptions.UserNotFoundException
            If the user does not exist
        """
        user = user_repository.get_one_or_none(
            attr=self._user_name_attribute,
            value=username,
        )

        if not user:
            msg = f"User '{username}' does not exist"
            logging.debug(msg)
            # Disable lines below for future implementation of logging and
            # unit of work commit
            # self.logger(msg=msg, level=LogLevel.DEBUG)
            # self.uow.commit()
            raise exceptions.UserNotFoundException(msg)

        return user

    def _verify_password(
        self,
        credentials: PasswordCredentials,
        user_repository: SqlRepository[User],
    ) -> User:
        """Verify the password for a user.

        Parameters
        ----------
        credentials
            Password credentials for the user
        user_repository
            The repository to query for the user

        Returns
        -------
            User instance representing the authenticated user

        Raises
        ------
        exceptions.InvalidCredentialsException
            If the provided credentials are invalid
        exceptions.MissingPasswordException
            If the user does not have a password set
        """

        user = self._get_user(credentials.username, user_repository)

        try:
            if not self._password_factory.verify_password(
                credentials.password, user.password
            ):
                msg = (
                    f"The provided password for user "
                    f"'{getattr(user, self._user_name_attribute)}' is "
                    "incorrect"
                )
                logging.debug(msg)
                # Disable lines below for future implementation of logging and
                # unit of work commit
                # self.logger(msg=msg, level=LogLevel.DEBUG)
                # self.uow.commit()
                raise exceptions.InvalidCredentialsException(msg)
        except exceptions.MissingPasswordException as exc:
            msg = (
                f"No password value to compare for "
                f"'{getattr(user, self._user_name_attribute)}'"
            )
            logging.error(msg)
            # Disable lines below for future implementation of logging and
            # unit of work commit
            # self.logger(msg=msg, level=LogLevel.ERROR)
            # self.uow.commit()
            raise exceptions.MissingPasswordException(msg) from exc

        return user

    def _update_user_password(
        self,
        user: User,
        new_password: str,
        user_repository: SqlRepository[User],
    ) -> None:
        """Change the password for a user.

        Parameters
        ----------
        user
            User instance representing the user to update the password for
        new_password
            The new password to set for the user
        user_repository
            The repository to query for the user
        """
        user = self._get_user(
            username=getattr(user, self._user_name_attribute),
            user_repository=user_repository,
        )

        user.password = self._password_factory.hash_password(new_password)
