"""Authentication service module."""

from alpha.domain.models.user import User
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token
from alpha.providers.models.credentials import PasswordCredentials
from alpha.interfaces.providers import IdentityProvider
from alpha import exceptions
from alpha.services.models.cookie import Cookie


class AuthenticationService:
    """This class is responsible for handling authentication operations in an
    application. It provides methods for user authentication, token, issuance,
    token validation, password change, pretending to login as another user,
    and merging user data with identity data.
    """

    def __init__(
        self,
        identity_provider: IdentityProvider,
        identity_id_attribute: str = "subject",
        use_cookies: bool = False,
        cookie_auth_token_name: str = "auth_token",
        cookie_refresh_token_name: str = "refresh_token",
        cookie_auth_token_max_age: int = 900,
        cookie_refresh_token_max_age: int = 3600 * 24 * 7,
        cookie_path: str = "/",
        cookie_domain: str | None = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: str = "Lax",
        merge_with_database_users: bool = False,
        user_id_attribute: str = "username",
        uow: UnitOfWork | None = None,
        users_repository_name: str = "users",
        static_user: User | None = None,
    ) -> None:
        """Initialize the AuthenticationService.

        Parameters
        ----------
        identity_provider
            Identity provider to use for authentication.
        identity_id_attribute, optional
            Attribute name in the identity to use as the unique identifier, by
            default "subject"
        use_cookies, optional
            Whether to use cookies for authentication, by default False
        cookie_auth_token_name, optional
            Name of the cookie to store the access token,
            by default "auth_token"
        cookie_refresh_token_name, optional
            Name of the cookie to store the refresh token,
            by default "refresh_token"
        cookie_auth_token_max_age, optional
            Maximum age of the access token cookie in seconds,
            by default 900
        cookie_refresh_token_max_age, optional
            Maximum age of the refresh token cookie in seconds,
            by default 3600 * 24 * 7
        cookie_path, optional
            Path for which the authentication cookies are valid,
            by default "/"
        cookie_domain, optional
            Domain for which the authentication cookies are valid,
            by default None
        cookie_secure, optional
            Whether the authentication cookies should be secure,
            by default True
        cookie_httponly, optional
            Whether the authentication cookies should be HTTP-only,
            by default True
        cookie_samesite, optional
            The SameSite attribute for the authentication cookies,
            by default "Lax"
        merge_with_database_users, optional
            Whether to merge identity data with database user data,
            by default False
        user_id_attribute, optional
            Attribute name in the user database to use as the unique
            identifier, by default "username"
        uow, optional
            UnitOfWork instance for database operations, by default None
        users_repository_name, optional
            Name of the user repository in the UnitOfWork, by default "users"
        static_user, optional
            Static user to use for authentication, by default None.
            If provided, this user will be authenticated if the credentials
            match, bypassing the identity provider. This can be used for
            development/testing or as a fallback user and should not be used in
            production environments.
        """
        self._identity_provider = identity_provider
        self._identity_id_attribute = identity_id_attribute
        self._use_cookies = use_cookies
        self._cookie_auth_token_name = cookie_auth_token_name
        self._cookie_refresh_token_name = cookie_refresh_token_name
        self._cookie_auth_token_max_age = cookie_auth_token_max_age
        self._cookie_refresh_token_max_age = cookie_refresh_token_max_age
        self._cookie_path = cookie_path
        self._cookie_domain = cookie_domain
        self._cookie_secure = cookie_secure
        self._cookie_httponly = cookie_httponly
        self._cookie_samesite = cookie_samesite
        self._merge_with_database_users = merge_with_database_users
        self._user_id_attribute = user_id_attribute
        self.uow = uow
        self._users_repository_name = users_repository_name
        self._static_user = static_user

    def login(self, credentials: PasswordCredentials) -> str | Cookie:
        """Authenticate a user by their credentials.

        Parameters
        ----------
        credentials
            Credentials to authenticate the user.

        Returns
        -------
            Authentication token as a string.
        """
        if (
            self._static_user
            and credentials.username == self._static_user.username
            and credentials.password == self._static_user.password
        ):
            identity = Identity.from_user(self._static_user)
        else:
            identity = self._identity_provider.authenticate(credentials)

            if self._merge_with_database_users and identity:
                identity = self._merge_identity_with_user(identity)

        token = self._identity_provider.issue_token(identity)
        if self._use_cookies:
            return self._create_auth_cookie(token)

        return token.value

    def logout(self, token: str) -> str | Cookie:
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
        if self._use_cookies:
            return self._create_logout_cookie()
        return "Logout successful"

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

    def refresh_token(self, refresh_token: str) -> str:
        """Refresh an authentication token using a refresh token. This method
        expects a stateful implementation where refresh tokens are stored and
        validated.

        Parameters
        ----------
        refresh_token
            Refresh token to use for refreshing the authentication token.

        Returns
        -------
            New authentication token as a string.

        Raises
        ------
        exceptions.UnauthorizedException
            If the refresh token is invalid.
        """
        raise NotImplementedError(
            "Refresh token functionality is not implemented yet"
        )

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
        if identity.has_admin_privileges is not True:
            raise exceptions.UnauthorizedException(
                "Only admin users can pretend to be another user"
            )

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
        """Merge User data into an Identity instance.

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
                self.uow, self._users_repository_name
            )
            user = users.get_by_id(
                value=getattr(identity, self._user_id_attribute),
                attr=self._user_id_attribute,
            )
            if user:
                identity.update_from_user(user)
            else:
                # Create new user from identity if not found in database
                user = User.from_identity(identity)
                users.add(user)
                self.uow.commit()
        return identity

    def _create_auth_cookie(self, token: Token) -> Cookie:
        """Create an authentication cookie for a token.

        Parameters
        ----------
        token
            Token to create the authentication cookie for.

        Returns
        -------
            Cookie object representing the authentication cookie.
        """
        return Cookie(
            key=self._cookie_auth_token_name,
            value=token.value,
            max_age=self._cookie_auth_token_max_age,
            path=self._cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=self._cookie_httponly,
            samesite=self._cookie_samesite,
        )

    def _create_logout_cookie(self) -> Cookie:
        """Create a cookie to clear the authentication cookie on logout.

        Returns
        -------
            Cookie object representing the logout cookie.
        """
        return Cookie(
            key=self._cookie_auth_token_name,
            operation="delete",
            path=self._cookie_path,
            domain=self._cookie_domain,
        )
