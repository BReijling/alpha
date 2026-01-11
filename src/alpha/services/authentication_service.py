"""Authentication service module."""

from alpha.domain.models.user import User
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token
from alpha.providers.models.credentials import PasswordCredentials
from alpha.interfaces.providers import IdentityProvider
from alpha import exceptions


class AuthenticationService:
    """Service for handling authentication operations."""

    def __init__(
        self,
        identity_provider: IdentityProvider,
        identity_id_attribute: str = "subject",
        merge_with_database_users: bool = False,
        user_id_attribute: str = "id",
        uow: UnitOfWork | None = None,
        repository_name: str = "users",
    ) -> None:
        """Initialize the AuthenticationService.

        Parameters
        ----------
        identity_provider
            Identity provider to use for authentication.
        identity_id_attribute, optional
            Attribute name in the identity to use as the unique identifier, by
            default "subject"
        merge_with_database_users, optional
            Whether to merge identity data with database user data, by default
            False
        user_id_attribute, optional
            Attribute name in the user database to use as the unique
            identifier, by default "id"
        uow, optional
            UnitOfWork instance for database operations, by default None
        repository_name, optional
            Name of the user repository in the UnitOfWork, by default "users"
        """
        self._identity_provider = identity_provider
        self._identity_id_attribute = identity_id_attribute
        self._merge_with_database_users = merge_with_database_users
        self._user_id_attribute = user_id_attribute
        self.uow = uow
        self._repository_name = repository_name

    def login(self, credentials: PasswordCredentials) -> str:
        """Authenticate a user by their credentials.

        Parameters
        ----------
        credentials
            Credentials to authenticate the user.

        Returns
        -------
            Authentication token as a string.
        """
        identity = self._identity_provider.authenticate(credentials)

        if self._merge_with_database_users and identity:
            identity = self._merge_identity_with_user(identity)

        token = self._identity_provider.issue_token(identity)
        return token.value

    def logout(self, token: str) -> str:
        """Logout a user by invalidating their token.

        Parameters
        ----------
        token
            Authentication token.

        Returns
        -------
            Confirmation message.

        Raises
        ------
        exceptions.UnauthorizedException
            If the token is invalid.
        """
        if not self._identity_provider.validate(Token(value=token)):
            raise exceptions.UnauthorizedException("Invalid token")
        return "Logged out"

    def verify(self, token: str) -> Identity:
        """Verify a token and return the associated identity.

        Parameters
        ----------
        token
            Authentication token.

        Returns
        -------
            Verified Identity instance.
        """
        return self._identity_provider.validate(Token(value=token))

    # def refresh_token(self, token: str) -> str:
    #     if not self._token_factory.validate(token):
    #         raise exceptions.UnauthorizedException("Invalid token")

    #     payload = self._token_factory.get_payload(token)
    #     user_id = payload.get(self._identity_id_attribute)
    #     if not user_id:
    #         raise exceptions.BadRequestException("Invalid token payload")

    #     return self._token_factory.create(user_id, payload)

    def change_password(
        self,
        credentials: PasswordCredentials,
        new_password: str,
    ) -> None:
        """Change the password for a user.

        Parameters
        ----------
        credentials
            Credentials to authenticate the user.
        new_password
            New password for the user.
        """
        if self._identity_provider.authenticate(credentials):
            self._identity_provider.change_password(credentials, new_password)

    def pretend_login(self, identity: Identity, pretend_subject: str) -> str:
        """Login as another user by pretending to be them.

        Parameters
        ----------
        identity
            Identity of the user who wants to pretend to be another user.
        pretend_subject
            Subject identifier of the user to pretend to be.

        Returns
        -------
            Authentication token as a string.

        Raises
        ------
        exceptions.NotFoundException
            If the user to pretend to be is not found.
        """
        pretend_identity = self._identity_provider.get_user(pretend_subject)
        if not pretend_identity:
            raise exceptions.NotFoundException("User not found")

        identity.pretend_identity = pretend_identity
        token = self._identity_provider.issue_token(identity)
        return token.value

    def _merge_identity_with_user(
        self,
        identity: Identity,
    ) -> Identity:
        """Merge User data into a Identity instance.

        Parameters
        ----------
        identity
            Identity object containing user information.

        Returns
        -------
            Updated Identity instance.
        """
        if not self.uow:
            raise exceptions.MissingDependencyException(
                "UnitOfWork is not configured for AuthenticationService"
            )

        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._repository_name
            )
            user = users.get_by_id(
                identity.subject, id_attribute=self._user_id_attribute
            )
            if not user:
                user = User.from_identity(identity)
                users.add(user)
            identity.update_from_user(user)
            self.uow.commit()
        return identity
