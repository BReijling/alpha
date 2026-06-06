"""Authentication service module."""

from datetime import datetime, timezone
from typing import NoReturn

from alpha.domain.models.group import Group
from alpha.domain.models.user import User
from alpha.infra.models.search_filter import Operator, SearchFilter
from alpha.interfaces.refresh_repository import RefreshRepository
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token
from alpha.providers.models.credentials import PasswordCredentials
from alpha.interfaces.providers import IdentityProvider
from alpha.repositories.refresh.memory_repository import (
    MemoryRefreshRepository,
)
from alpha.utils.cookie import Cookie
from alpha import exceptions


class AuthenticationService:
    """This class is responsible for handling authentication operations in an
    application. It provides methods for user authentication, token issuance,
    token validation, password change, revoking tokens, pretending to login as
    another user and merging user data with identity data.

    The service is designed to be flexible and configurable, allowing you to
    customize various aspects of the authentication process, such as cookie
    management and integration with different identity providers. It can be
    used in a variety of applications, including web applications, APIs, and
    microservices, to provide a consistent and secure authentication
    experience.

    The service supports both stateless and stateful authentication mechanisms,
    allowing you to choose the approach that best fits your application's
    needs. Stateless authentication can be achieved using tokens (e.g., JWTs)
    that are self-contained and do not require server-side storage, while
    stateful authentication can be implemented using refresh tokens that
    require server-side storage and management. The service can also be
    configured to merge identity data with user and group data from a database,
    providing a unified view of the authenticated user's information and
    permissions.

    Refresh tokens can be stored using different mechanisms. By default, the
    service uses an in-memory repository for refresh tokens, which is suitable
    for development and testing purposes. However, for production use, it is
    recommended to implement a more robust storage mechanism, such as a
    database-backed repository, to ensure that refresh tokens are persisted and
    can be reliably managed across application restarts and deployments.
    """

    def __init__(
        self,
        identity_provider: IdentityProvider,
        identity_id_attribute: str = "subject",
        use_cookies: bool = False,
        use_refresh_tokens: bool = False,
        cookie_auth_token_name: str = "auth_token",
        cookie_refresh_token_name: str = "refresh_token",
        cookie_path: str = "/",
        cookie_domain: str | None = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: str = "Lax",
        auth_token_max_age: int = 900,
        refresh_token_max_age: int = 3600 * 24 * 7,
        merge_with_database_users: bool = False,
        merge_with_database_groups: bool = False,
        user_username_attribute: str = "username",
        group_name_attribute: str = "name",
        uow: UnitOfWork | None = None,
        user_model: type[User] = User,
        group_model: type[Group] = Group,
        token_model: type[Token] = Token,
        users_repository_name: str = "users",
        groups_repository_name: str = "groups",
        refresh_repository: RefreshRepository | None = None,
        refresh_identity_on_refresh: bool = False,
        static_user: User | None = None,
    ) -> None:
        """Initialize the AuthenticationService with the provided
        configuration.

        Parameters
        ----------
        identity_provider
            Identity provider to use for authentication.
        identity_id_attribute
            Attribute name in the identity to use as the unique identifier, by
            default "subject"
        use_cookies
            Whether to use cookies for authentication, by default False
        use_refresh_tokens
            Whether to use refresh tokens for authentication, by default False.
            Enabling this option requires use_cookies to be True, since refresh
            tokens are typically stored in cookies. This parameter needs to be
            set to True if you want to use refresh tokens for maintaining user
            sessions without requiring them to log in again, while still
            ensuring that access tokens have a limited lifespan for security
            purposes.
        cookie_auth_token_name
            Name of the cookie to store the access token,
            by default "auth_token"
        cookie_refresh_token_name
            Name of the cookie to store the refresh token,
            by default "refresh_token"
        cookie_path
            Path for which the authentication cookies are valid,
            by default "/"
        cookie_domain
            Domain for which the authentication cookies are valid,
            by default None
        cookie_secure
            Whether the authentication cookies should be secure,
            by default True
        cookie_httponly
            Whether the authentication cookies should be HTTP-only,
            by default True
        cookie_samesite
            The SameSite attribute for the authentication cookies,
            by default "Lax"
        auth_token_max_age
            Maximum age of the access token cookie in seconds,
            by default 900
        refresh_token_max_age
            Maximum age of the refresh token cookie in seconds,
            by default 3600 * 24 * 7
        merge_with_database_users
            Whether to merge identity data with database user data,
            by default False
        merge_with_database_groups
            Whether to merge identity data with database group data,
            by default False
        user_username_attribute
            Attribute name in the user database to use as the unique
            identifier, by default "username"
        group_name_attribute
            Attribute name in the group database to use as the unique
            identifier, by default "name"
        uow
            UnitOfWork instance for database operations, by default None
        user_model
            User model class to use for database operations, by default User
        group_model
            Group model class to use for database operations, by default Group
        token_model
            Token model class to use for database operations, by default Token
        users_repository_name
            Name of the user repository in the UnitOfWork, by default "users"
        groups_repository_name
            Name of the group repository in the UnitOfWork, by default "groups"
        refresh_repository
            Refresh token repository instance, by default None. If not
            provided, the service will use the MemoryRefreshRepository and
            forward the token_model and refresh_token_max_age parameters to it.
            This allows for flexibility in how refresh tokens are stored and
            managed, enabling the use of different storage mechanisms as needed
            without being tied to a specific implementation. The
            MemoryRefreshRepository is suitable for development and testing
            purposes, but for production use, it is recommended to implement a
            more robust storage mechanism, such as a database-backed
            repository, to ensure that refresh tokens are persisted and can be
            reliably managed across application restarts and deployments. If
            you choose to provide your own implementation of the
            RefreshRepository, make sure it adheres to the expected interface
            and behavior for managing refresh tokens in the context of this
            authentication service.
        refresh_identity_on_refresh
            Whether to refresh the identity when refreshing the token, by
            default False. This need to be implemented in the
            identity provider's issue_token method. This usually requires
            additional authorization from the identity service.
        static_user
            Static user to use for authentication, by default None.
            If provided, this user will be authenticated if the credentials
            match, bypassing the identity provider. This can be used for
            development/testing or as a fallback user and should not be used in
            production environments.

        Raises
        ------
        ValueError
            If refresh tokens are enabled without using cookies, or if an
            invalid configuration is detected.
        """
        self._identity_provider = identity_provider
        self._identity_id_attribute = identity_id_attribute
        self._use_cookies = use_cookies
        self._use_refresh_tokens = use_refresh_tokens
        self._cookie_auth_token_name = cookie_auth_token_name
        self._cookie_refresh_token_name = cookie_refresh_token_name
        self._cookie_path = cookie_path
        self._cookie_domain = cookie_domain
        self._cookie_secure = cookie_secure
        self._cookie_httponly = cookie_httponly
        self._cookie_samesite = cookie_samesite
        self._auth_token_max_age = auth_token_max_age
        self._refresh_token_max_age = refresh_token_max_age
        self._merge_with_database_users = merge_with_database_users
        self._merge_with_database_groups = merge_with_database_groups
        self._user_username_attribute = user_username_attribute
        self._group_name_attribute = group_name_attribute
        self.uow = uow
        self._user_model = user_model
        self._group_model = group_model
        self._token_model = token_model
        self._users_repository_name = users_repository_name
        self._groups_repository_name = groups_repository_name
        self._refresh_repository = (
            refresh_repository
            or MemoryRefreshRepository(
                token_model=token_model,
                token_max_age_seconds=refresh_token_max_age,
            )
        )
        self._refresh_identity_on_refresh = refresh_identity_on_refresh
        self._static_user = static_user

        if self._use_refresh_tokens and not self._use_cookies:
            raise ValueError(
                "Refresh tokens can only be used when use_cookies is True"
            )

        self._in_memory_refresh_tokens: dict[str, Token] = {}

    def login(
        self, credentials: PasswordCredentials
    ) -> str | tuple[Cookie, str] | tuple[Cookie, Cookie, str]:
        """Authenticate a user by their credentials. The identity provider is
        used to authenticate the user and retrieve their identity. An
        authentication token is then issued for the authenticated identity. If
        configured to use cookies, the token is also stored in a cookie. If
        configured to use refresh tokens, a refresh token is also created and
        stored in a cookie.

        The identity can optionally be merged with user and group data from the
        database, based on the configuration settings and the supplied unit of
        work.

        Parameters
        ----------
        credentials
            Credentials to authenticate the user.

        Returns
        -------
        str
            Authentication token as a string or a tuple containing a Cookie
            object and the token string.
        tuple[Cookie, str]
            tuple containing a Cookie object and the token string if using
            cookies without refresh tokens.
        tuple[Cookie, Cookie, str]
            tuple containing two Cookie objects and the token string if using
            cookies with refresh tokens.
        """
        # Check if static user is configured and matches the provided
        # credentials
        if (
            self._static_user
            and self._static_user.username is not None
            and self._static_user.password is not None
            and credentials.username == self._static_user.username
            and credentials.password == self._static_user.password
        ):
            identity = Identity.from_user(self._static_user)

        # Use the identity provider to authenticate the user and retrieve their
        # identity
        else:
            identity = self._identity_provider.authenticate(credentials)

        # If configured to merge with database users and groups, perform the
        # merge operations on the retrieved identity.
        if self._merge_with_database_users and identity:
            identity = self._merge_identity_with_user(identity)
        if self._merge_with_database_groups and identity:
            identity = self._merge_identity_with_groups(identity)

        # Issue an authentication token for the authenticated identity
        token = self._identity_provider.issue_token(identity)

        if not self._use_cookies:
            return str(token)

        # If using cookies, create an authentication cookie for the token and
        # return it along with the token string.
        auth_cookie = self._create_token_cookie(
            token, self._cookie_auth_token_name, self._auth_token_max_age
        )

        if not self._use_refresh_tokens:
            return auth_cookie, str(token)

        # If using refresh tokens, also create a refresh token and cookie.
        refresh_token = self._refresh_repository.create(
            subject=getattr(identity, self._identity_id_attribute)
        )
        refresh_cookie = self._create_token_cookie(
            refresh_token,
            self._cookie_refresh_token_name,
            self._refresh_token_max_age,
        )
        return auth_cookie, refresh_cookie, str(token)

    def logout(
        self, refresh_token: str | None = None
    ) -> tuple[Cookie, str] | tuple[Cookie, Cookie, str]:
        """Logout a user by invalidating their token.

        Parameters
        ----------
        refresh_token
            Optional refresh token to invalidate along with the authentication
            token. This is only applicable if using refresh tokens.

        Returns
        -------
        tuple[Cookie, str]
            Confirmation message. If using cookies, returns a Cookie object to
            clear the authentication cookie.
        tuple[Cookie, Cookie, str]
            Confirmation message. If using cookies with refresh tokens, returns
            Cookie objects to clear both the authentication and refresh token
            cookies.

        Raises
        ------
        NotImplementedError
            Token invalidation is not implemented for non-cookie
            authentication.
        """
        if not self._use_cookies:
            raise NotImplementedError(
                "Token invalidation is not implemented for non-cookie "
                "authentication"
            )

        logout_auth_cookie = self._create_logout_cookie(
            self._cookie_auth_token_name
        )
        if not self._use_refresh_tokens:
            return logout_auth_cookie, "Logout successful"

        logout_refresh_cookie = self._create_logout_cookie(
            self._cookie_refresh_token_name
        )

        if refresh_token:
            try:
                self._refresh_repository.delete(refresh_token)
            except exceptions.NotFoundException:
                # If the refresh token is not found in the repository, we can
                # ignore it since the goal is to ensure that the token is
                # invalidated. If it's not found, it means it has already been
                # invalidated or never existed.
                pass

        return (
            logout_auth_cookie,
            logout_refresh_cookie,
            "Logout successful",
        )

    def verify(self, auth_token: str) -> Identity:
        """Verify an auth_token and return the associated identity.

        Parameters
        ----------
        auth_token
            Authentication token.

        Returns
        -------
        Identity
            Verified Identity instance.
        """
        return self._identity_provider.validate(Token(value=auth_token))

    def refresh_token(
        self, refresh_token: str, auth_token: str | None = None
    ) -> tuple[Cookie, str]:
        """Refresh an authentication token using a refresh token. This method
        expects a stateful implementation where refresh tokens are stored and
        validated.

        Parameters
        ----------
        refresh_token
            Refresh token to use for refreshing the authentication token.
        auth_token
            Optional current authentication token, which can be reused if
            needed.

        Returns
        -------
        tuple[Cookie, str]
            A tuple containing a Cookie object for the new authentication token
            and the token string.

        Raises
        ------
        exceptions.MissingConfigurationException
            If refresh token authentication is not properly configured.
        exceptions.UnauthorizedException
            If the refresh token is invalid, expired, or the identity cannot be
            retrieved.
        """
        if not self._use_cookies or not self._use_refresh_tokens:
            raise exceptions.MissingConfigurationException(
                "Refresh token authentication is not enabled. Both "
                "use_cookies and use_refresh_tokens must be True."
            )

        # Retrieve the stored refresh token from the repository using the
        # provided refresh token string.
        try:
            stored_refresh_token = self._refresh_repository.get(refresh_token)
        except exceptions.NotFoundException:
            raise exceptions.UnauthorizedException("Invalid refresh token")

        # Verify the refresh token and raise an exception if it's invalid or
        # expired.
        self._verify_refresh_token(stored_refresh_token)

        # Set default identity to None.
        identity = None

        if self._refresh_identity_on_refresh:
            if stored_refresh_token.subject is None:
                raise exceptions.UnauthorizedException(
                    "Invalid refresh token: no subject"
                )
            identity = self._identity_provider.get_user(
                subject=stored_refresh_token.subject
            )
            # If configured to merge with database users and groups, perform
            # the merge operations on the identity.
            if self._merge_with_database_users:
                identity = self._merge_identity_with_user(identity)
            if self._merge_with_database_groups:
                identity = self._merge_identity_with_groups(identity)

        # If an auth token is provided and the identity could not be retrieved
        # using the refresh token, attempt to retrieve the identity from the
        # auth token.
        if auth_token and not identity:
            if not self._identity_provider.token_factory or not hasattr(
                self._identity_provider.token_factory, "get_payload"
            ):
                raise exceptions.MissingConfigurationException(
                    "Identity provider does not have a token factory "
                    "configured, cannot retrieve identity from auth token."
                )
            try:
                # Attempt to retrieve the identity from the auth token without
                # validating the token, since it may be expired. The payload
                # should still be retrievable if the token is expired, as long
                # as the signature is valid. If the signature is invalid, an
                # exception will be raised and caught, resulting in the
                # identity remaining None.
                payload = self._identity_provider.token_factory.get_payload(
                    token=auth_token, options={"verify_exp": False}
                )
                identity = Identity.from_dict(payload)
            except Exception:
                identity = None

        if not identity:
            raise exceptions.UnauthorizedException(
                "Invalid identity for refresh token"
            )

        token = self._identity_provider.issue_token(identity)

        auth_cookie = self._create_token_cookie(
            token, self._cookie_auth_token_name, self._auth_token_max_age
        )
        return auth_cookie, str(token)

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

    def revoke_tokens(self, identity: Identity, subject: str) -> None:
        """Revoke all refresh tokens for a given subject.

        All refresh tokens associated with the specified subject will be
        deleted from the refresh token repository, effectively revoking any
        active sessions.

        To be able to use this method, the authenticated identity must have
        admin privileges. This is a powerful operation that should be used with
        caution, as it will terminate all active sessions for the specified
        subject. After revocation, users will need to log in again to obtain
        new tokens and regain access. Users who are currently logged in with
        valid access tokens may still have access until their access tokens
        expire, but they will not be able to refresh their tokens or obtain new
        ones without logging in again. This method is typically used in
        scenarios where a user's credentials have been compromised or when an
        administrator needs to enforce a logout for security reasons.

        Parameters
        ----------
        identity
            Identity of the user attempting to revoke tokens.
        subject
            Subject identifier for which to revoke tokens.
        """
        if identity.has_admin_privileges is not True:
            raise exceptions.ForbiddenException(
                "Only admin users can revoke tokens for a subject"
            )

        self._refresh_repository.delete_all(subject)

    def pretend_login(
        self, identity: Identity, pretend_subject: str
    ) -> str | tuple[Cookie, str]:
        """Login as another user by pretending to be them.

        The identity provider is used to retrieve the identity of the user to
        pretend to be. An authentication token is then issued for the pretended
        identity. If configured to use cookies, the token is also stored in a
        cookie.

        To be able to use this method, the authenticated identity must have
        admin privileges. The identity provider has to be able to retrieve the
        identity of the user to pretend to be. Generally this means that the
        identity provider needs to have access to the user's information. This
        requires admin privileges on the identity provider side, so this method
        should only be used in trusted environments.

        Parameters
        ----------
        identity
            Identity of the user who wants to pretend to be another user.
        pretend_subject
            Subject identifier of the user to pretend to be.

        Returns
        -------
        str
            Authentication token as a string.
        tuple[Cookie, str]
            A tuple containing a Cookie object and the token string if using
            cookies.

        Raises
        ------
        exceptions.NotFoundException
            If the user to pretend to be is not found.
        """
        if identity.has_admin_privileges is not True:
            raise exceptions.ForbiddenException(
                "Only admin users can pretend to be another user"
            )

        pretend_identity = self._identity_provider.get_user(pretend_subject)

        if not pretend_identity:
            raise exceptions.NotFoundException("User not found")

        identity.pretend_identity = pretend_identity
        token = self._identity_provider.issue_token(identity)

        if not self._use_cookies:
            return str(token)

        auth_cookie = self._create_token_cookie(
            token, self._cookie_auth_token_name, self._auth_token_max_age
        )
        return auth_cookie, str(token)

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
        Identity
            Updated Identity instance.
        """
        if self.uow is None:
            self._raise_no_uow()

        with self.uow:
            users: SqlRepository[User] = getattr(
                self.uow, self._users_repository_name
            )

            user = users.get_by_id(
                value=getattr(identity, self._user_username_attribute),
                attr=self._user_username_attribute,
            )
            if user:
                identity.update_from_user(user)

            else:
                # Create new user from identity if not found in database
                user = self._user_model.from_identity(identity)
                users.add(user)
                self.uow.commit()

        return identity

    def _merge_identity_with_groups(
        self,
        identity: Identity,
    ) -> Identity:
        """Merge Group data into an Identity instance.

        Parameters
        ----------
        identity
            Identity object containing group information.

        Returns
        -------
        Identity
            Updated Identity instance.
        """
        if self.uow is None:
            self._raise_no_uow()

        with self.uow:
            groups_repo: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )

            groups = list(identity.groups)
            for i, group in enumerate(groups):
                if isinstance(group, self._group_model):
                    groups[i] = getattr(group, self._group_name_attribute)

            filters = [
                SearchFilter(
                    field=self._group_name_attribute,
                    op=Operator.IN,
                    value=groups,
                )
            ]
            user_groups = groups_repo.select(filters=filters)
            identity.update_from_groups(user_groups)

        return identity

    def _create_token_cookie(
        self, token: Token, cookie_name: str, max_age: int
    ) -> Cookie:
        """Create a cookie for a token.

        Parameters
        ----------
        token
            Token to create the cookie for.
        cookie_name
            Name of the cookie.
        max_age
            Maximum age of the cookie in seconds.

        Returns
        -------
        Cookie
            Cookie object representing the cookie.
        """
        return Cookie(
            key=cookie_name,
            value=token.value,
            max_age=max_age,
            path=self._cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=self._cookie_httponly,
            samesite=self._cookie_samesite,
        )

    def _create_logout_cookie(self, cookie_name: str) -> Cookie:
        """Create a cookie to clear the authentication cookie on logout.

        Parameters
        ----------
        cookie_name
            The name of the cookie to clear.

        Returns
        -------
        Cookie
            Cookie object representing the logout cookie.
        """
        return Cookie(
            key=cookie_name,
            operation="delete",
            path=self._cookie_path,
            domain=self._cookie_domain,
        )

    def _raise_no_uow(self) -> NoReturn:
        """Raise an exception if the UnitOfWork is not configured.

        Raises
        ------
        exceptions.MissingDependencyException
            If the UnitOfWork is not configured for the AuthenticationService.
        """
        raise exceptions.MissingDependencyException(
            "UnitOfWork is not configured for AuthenticationService"
        )

    def _verify_refresh_token(self, token: Token | None) -> NoReturn | None:
        """Verify the validity of a refresh token.

        Parameters
        ----------
        token
            The refresh token to verify.

        Raises
        ------
        exceptions.UnauthorizedException
            If the refresh token is invalid or has expired.
        """
        if not token or token.token_type != "Refresh":
            raise exceptions.UnauthorizedException("Invalid refresh token")
        elif token.expires_at is None or token.expires_at < datetime.now(
            tz=timezone.utc
        ):
            raise exceptions.TokenExpiredException("Refresh token has expired")
        return None
