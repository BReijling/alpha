"""This module contains interfaces for various types of identity providers."""

from typing import ClassVar, Protocol, runtime_checkable

from alpha.interfaces.token_factory import TokenFactory
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token


@runtime_checkable
class PasswordAuthenticator(Protocol):
    """Password-based authenticator interface.

    Intended for providers that authenticate users based on username and password
    credentials.

    For example, LDAP, Active Directory or database-backed authentication.
    """

    def authenticate(
        self,
        credentials: PasswordCredentials,
    ) -> Identity:
        """Method to authenticate a user based on username and password.

        Parameters
        ----------
        credentials
            Object containing username and password.

        Returns
        -------
            Identity object representing the authenticated user.
        """
        ...


@runtime_checkable
class TokenValidator(Protocol):
    """Token validation interface

    Intended for providers that validate tokens, such as JWTs or OAuth tokens.

    For example, JWT token validation against public keys, OAuth token
    introspection, etc.
    """

    def validate(
        self,
        token: Token,
    ) -> Identity:
        """Method to validate a token and return the associated identity.

        Parameters
        ----------
        token
            Token object to be validated.

        Returns
        -------
            Identity object representing the validated token.
        """
        ...


@runtime_checkable
class TokenIssuer(Protocol):
    """Token issuance interface.

    Intended for providers that issue tokens for authenticated identities.

    For example, JWT token issuance, OAuth token generation, etc.
    """

    def issue_token(
        self,
        identity: Identity,
    ) -> Token:
        """Method to issue a token for a given identity.

        Parameters
        ----------
        identity
            Identity object for which the token is to be issued.

        Returns
        -------
            Token object representing the issued token.
        """
        ...


@runtime_checkable
class UserDirectory(Protocol):
    """User directory interface.

    Intended for providers that manage and retrieve user information.

    For example, LDAP user directory, database-backed user store, etc.
    """

    def get_user(
        self,
        subject: str,
    ) -> Identity:
        """Method to retrieve the identity of a subject.

        Parameters
        ----------
        subject
            Unique identifier of the user to retrieve.

        Returns
        -------
            Identity object representing the subject.
        """
        ...


@runtime_checkable
class PasswordChanger(Protocol):
    """Password change interface.

    Intended for providers that support changing user passwords.
    """

    def change_password(
        self,
        credentials: PasswordCredentials,
        new_password: str,
    ) -> None:
        """Method to change the password for a given user.

        Parameters
        ----------
        credentials
            Object containing username and current password.
        new_password
            The new password to set for the user.

        Returns
        -------
            None
        """
        ...


@runtime_checkable
class TokenProvider(TokenValidator, TokenIssuer, Protocol):
    """Token provider interface.

    Intended for providers that handle token-related operations,
    such as issuing and validating tokens.
    """

    _token_factory: ClassVar[TokenFactory | None]


@runtime_checkable
class IdentityProvider(
    PasswordAuthenticator,
    TokenProvider,
    UserDirectory,
    PasswordChanger,
    Protocol,
):
    """Composite interface for identity providers.

    Combines password authentication, token validation, token issuance,
    and user directory functionalities into a single interface.
    """

    protocol: ClassVar[str]
