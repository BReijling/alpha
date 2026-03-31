"""Authentication service module."""

import os
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, NoReturn

from alpha.domain.models.group import Group
from alpha.domain.models.user import User
from alpha.infra.models.search_filter import Operator, SearchFilter
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token
from alpha.providers.models.credentials import PasswordCredentials
from alpha.interfaces.providers import IdentityProvider
from alpha.services.models.cookie import Cookie
from alpha.utils.secret_generator import generate_secret
from alpha import exceptions


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
        user_id_attribute: str = "username",
        group_id_attribute: str = "name",
        uow: UnitOfWork | None = None,
        users_repository_name: str = "users",
        groups_repository_name: str = "groups",
        refresh_token_storage: Literal[
            "database",
            "memory",
            "cache",
            "file",
        ] = "file",
        refresh_token_repository_name: str = "refresh_tokens",
        refresh_token_storage_file_path: str | None = None,
        refresh_token_length: int = 32,
        refresh_identity_on_refresh: bool = False,
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
        use_refresh_tokens, optional
            Whether to use refresh tokens for authentication, by default False
        cookie_auth_token_name, optional
            Name of the cookie to store the access token,
            by default "auth_token"
        cookie_refresh_token_name, optional
            Name of the cookie to store the refresh token,
            by default "refresh_token"
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
        auth_token_max_age, optional
            Maximum age of the access token cookie in seconds,
            by default 900
        refresh_token_max_age, optional
            Maximum age of the refresh token cookie in seconds,
            by default 3600 * 24 * 7
        merge_with_database_users, optional
            Whether to merge identity data with database user data,
            by default False
        merge_with_database_groups, optional
            Whether to merge identity data with database group data,
            by default False
        user_id_attribute, optional
            Attribute name in the user database to use as the unique
            identifier, by default "username"
        group_id_attribute, optional
            Attribute name in the group database to use as the unique
            identifier, by default "name"
        uow, optional
            UnitOfWork instance for database operations, by default None
        users_repository_name, optional
            Name of the user repository in the UnitOfWork, by default "users"
        groups_repository_name, optional
            Name of the group repository in the UnitOfWork, by default "groups"
        refresh_token_storage, optional
            Storage mechanism for refresh tokens, by default "file". Supported
            values are "database", "memory", "cache", and "file".
        refresh_token_repository_name, optional
            Name of the refresh token repository in the UnitOfWork,
            by default "refresh_tokens"
        refresh_token_storage_file_path, optional
            File path for storing refresh tokens if using file storage,
            by default None. This is required if refresh_token_storage is set
            to "file". When the value is None the file will be stored in the
            current working directory. The file should be a JSON file that
            stores an object of refresh tokens. If the file does not exist, it
            will be created automatically. The structure of the JSON file
            should be as follows:
            {
                "<TOKEN_VALUE>": {
                    "value": "<TOKEN_VALUE>",
                    "token_type": "Refresh",
                    "subject": "<SUBJECT>",
                    "created_at": "<ISO8601_DATETIME>",
                    "expires_at": "<ISO8601_DATETIME>"
                },
                ...
            }
        refresh_token_length, optional
            Length of the generated refresh tokens, by default 32
        refresh_identity_on_refresh, optional
            Whether to refresh the identity when refreshing the token, by
            default False. This need to be implemented in the
            identity provider's issue_token method. This usually requires
            additional authorization from the identity service.
        static_user, optional
            Static user to use for authentication, by default None.
            If provided, this user will be authenticated if the credentials
            match, bypassing the identity provider. This can be used for
            development/testing or as a fallback user and should not be used in
            production environments.

        Raises
        ------
        ValueError
            If refresh tokens are enabled without using cookies, or if an invalid
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
        self._user_id_attribute = user_id_attribute
        self._group_id_attribute = group_id_attribute
        self.uow = uow
        self._users_repository_name = users_repository_name
        self._groups_repository_name = groups_repository_name
        self._refresh_token_storage = refresh_token_storage
        self._refresh_token_repository_name = refresh_token_repository_name
        self._refresh_token_storage_file_path = (
            refresh_token_storage_file_path or "refresh_tokens.json"
        )
        self._refresh_token_length = refresh_token_length
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

        Parameters
        ----------
        credentials
            Credentials to authenticate the user.

        Returns
        -------
            Authentication token as a string or a tuple containing a Cookie
            object and the token string.
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
        refresh_token = self._create_refresh_token(
            subject=getattr(identity, self._identity_id_attribute)
        )
        refresh_cookie = self._create_token_cookie(
            refresh_token,
            self._cookie_refresh_token_name,
            self._refresh_token_max_age,
        )
        return auth_cookie, refresh_cookie, str(token)

    def logout(self, token: str) -> tuple[Cookie, str]:
        """Logout a user by invalidating their token.

        Parameters
        ----------
        token
            Authentication token.

        Returns
        -------
            Confirmation message. If using cookies, returns a Cookie object to
            clear the authentication cookie.

        Raises
        ------
        NotImplementedError
            If token invalidation is not implemented for non-cookie
            authentication.
        """
        if self._use_cookies:
            return self._create_logout_cookie(), "Logout successful"

        raise NotImplementedError(
            "Token invalidation is not implemented for non-cookie"
            " authentication"
        )

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

    def refresh_token(
        self, refresh_token: str, identity: Identity | None = None
    ) -> tuple[Cookie, str]:
        """Refresh an authentication token using a refresh token. This method
        expects a stateful implementation where refresh tokens are stored and
        validated.

        Parameters
        ----------
        refresh_token
            Refresh token to use for refreshing the authentication token.
        identity, optional
            Optional current identity, which can be reused if needed.

        Returns
        -------
            A tuple containing a Cookie object for the new authentication token
            and the token string.

        Raises
        ------
        exceptions.MissingConfigurationException
            If refresh token authentication is not properly configured.
        exceptions.UnauthorizedException
            If the refresh token is invalid.
        """
        if not self._use_cookies or not self._use_refresh_tokens:
            raise exceptions.MissingConfigurationException(
                "Refresh token authentication is not enabled. Both use_cookies "
                "and use_refresh_tokens must be True."
            )

        stored_refresh_token = self._get_refresh_token_from_storage(
            refresh_token
        )

        if self._refresh_identity_on_refresh:
            if stored_refresh_token.subject is None:
                raise exceptions.UnauthorizedException(
                    "Invalid refresh token: no subject"
                )
            identity = self._identity_provider.get_user(
                subject=stored_refresh_token.subject
            )

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

    def pretend_login(
        self, identity: Identity, pretend_subject: str
    ) -> str | tuple[Cookie, str]:
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
            Updated Identity instance.
        """
        if self.uow is None:
            self._raise_no_uow()

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
            Updated Identity instance.
        """
        if self.uow is None:
            self._raise_no_uow()

        with self.uow:
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )

            filters = [
                SearchFilter(
                    field=self._group_id_attribute,
                    op=Operator.IN,
                    value=identity.groups,
                )
            ]
            user_groups = groups.select(filters=filters)
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

    def _create_refresh_token(self, subject: str) -> Token:
        """Create and store a refresh token for a subject.

        Parameters
        ----------
        subject
            Subject identifier to create the refresh token for.

        Returns
        -------
            Token object representing the refresh token.
        """
        token = Token(
            value=generate_secret(self._refresh_token_length),
            token_type="Refresh",
            subject=subject,
            expires_at=datetime.now(tz=timezone.utc)
            + timedelta(seconds=self._refresh_token_max_age),
        )

        if self._refresh_token_storage == "database":
            token = self._store_refresh_token_to_database(token)

        elif self._refresh_token_storage == "file":
            self._store_refresh_token_to_file(token)

        elif self._refresh_token_storage == "memory":
            self._store_refresh_token_to_memory(token)

        elif self._refresh_token_storage == "cache":
            # Implement cache storage for refresh tokens if needed
            raise NotImplementedError(
                "Cache refresh token storage is not implemented yet"
            )

        else:
            raise exceptions.InvalidAttributeError(
                "Invalid refresh token storage mechanism. Configured storage"
                " mechanism is not supported. Check the configuration of the"
                " AuthenticationService."
            )

        return token

    def _store_refresh_token_to_database(self, token: Token) -> Token:
        """Store a refresh token in the database.

        Parameters
        ----------
        token
            Token object representing the refresh token to store.

        Returns
        -------
            The stored Token object.

        Raises
        ------
        exceptions.MissingDependencyException
            If the UnitOfWork is not configured for the AuthenticationService.
        """
        if self.uow is None:
            self._raise_no_uow()

        with self.uow:
            refresh_tokens: SqlRepository[Token] = getattr(
                self.uow, self._refresh_token_repository_name
            )
            token = refresh_tokens.add(token)
            self.uow.commit()

        return token

    def _store_refresh_token_to_file(self, token: Token) -> None:
        """Store a refresh token in a file.

        Parameters
        ----------
        token
            Token object representing the refresh token to store.

        Returns
        -------
            The stored Token object.

        Raises
        ------
        exceptions.ServerErrorException
            If the refresh token storage file is not found.
        """
        if not os.path.exists(self._refresh_token_storage_file_path):
            with open(self._refresh_token_storage_file_path, "w") as f:
                json.dump({}, f)

        with open(self._refresh_token_storage_file_path, "r") as f:
            tokens_data = json.load(f)

        tokens_data[token.value] = token.to_dict()

        with open(self._refresh_token_storage_file_path, "w") as f:
            json.dump(tokens_data, f, indent=4)

    def _store_refresh_token_to_memory(self, token: Token) -> None:
        """Store a refresh token in in-memory storage.

        Parameters
        ----------
        token
            Token object representing the refresh token to store.
        """
        self._in_memory_refresh_tokens[token.value] = token

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

    def _get_refresh_token_from_storage(self, refresh_token: str) -> Token:
        """Retrieve a refresh token from the configured storage mechanism.

        Parameters
        ----------
        refresh_token
            Refresh token string to retrieve.

        Returns
        -------
            Token object representing the refresh token.
        """
        if self._refresh_token_storage == "database":
            token = self._get_refresh_token_from_database(refresh_token)

        elif self._refresh_token_storage == "file":
            token = self._get_refresh_token_from_file(refresh_token)

        elif self._refresh_token_storage == "memory":
            token = self._get_refresh_token_from_memory(refresh_token)

        elif self._refresh_token_storage == "cache":
            # Implement cache retrieval for refresh tokens if needed
            raise NotImplementedError(
                "Cache refresh token storage is not implemented yet"
            )

        else:
            raise exceptions.InvalidAttributeError(
                "Invalid refresh token storage mechanism. Configured storage"
                " mechanism is not supported. Check the configuration of the"
                " AuthenticationService."
            )

        token = self._verify_refresh_token(token)
        return token

    def _get_refresh_token_from_database(
        self, refresh_token: str
    ) -> Token | None:
        """Retrieve a refresh token from the database.

        Parameters
        ----------
        refresh_token
            The refresh token string to retrieve.

        Returns
        -------
            The retrieved refresh token, or None if not found.
        """
        if self.uow is None:
            self._raise_no_uow()

        with self.uow:
            refresh_tokens: SqlRepository[Token] = getattr(
                self.uow, self._refresh_token_repository_name
            )
            token = refresh_tokens.get_one_or_none(
                attr="value", value=refresh_token
            )

        return token

    def _get_refresh_token_from_file(self, refresh_token: str) -> Token | None:
        """Retrieve a refresh token from a file.

        Parameters
        ----------
        refresh_token
            The refresh token string to retrieve.

        Returns
        -------
            The retrieved refresh token, or None if not found.

        Raises
        ------
        exceptions.ServerErrorException
            If the refresh token storage file is not found.
        """
        if not os.path.exists(self._refresh_token_storage_file_path):
            raise exceptions.ServerErrorException(
                "Refresh token storage file not found"
            )

        with open(self._refresh_token_storage_file_path, "r") as f:
            tokens_data: dict[str, dict[str, Any]] = json.load(f)

        token_data = tokens_data.get(refresh_token)
        if not token_data:
            return None

        return Token.from_dict(token_data)

    def _get_refresh_token_from_memory(
        self, refresh_token: str
    ) -> Token | None:
        """Retrieve a refresh token from in-memory storage.

        Parameters
        ----------
        refresh_token
            The refresh token string to retrieve.

        Returns
        -------
            The retrieved refresh token, or None if not found.
        """
        token = self._in_memory_refresh_tokens.get(refresh_token)

        return token

    def _verify_refresh_token(self, token: Token | None) -> Token:
        """Verify the validity of a refresh token.

        Parameters
        ----------
        token
            The refresh token to verify.

        Returns
        -------
            The verified refresh token.

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
        return token
