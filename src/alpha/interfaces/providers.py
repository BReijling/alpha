"""This module contains interfaces for various types of identity providers."""

from typing import Protocol

from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token


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


class IdentityProvider(
    PasswordAuthenticator, TokenValidator, TokenIssuer, UserDirectory, Protocol
):
    """Composite interface for identity providers.

    Combines password authentication, token validation, token issuance,
    and user directory functionalities into a single interface.
    """

    ...
