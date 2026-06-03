from typing import Protocol

from alpha.providers.models.token import Token


class RefreshRepository(Protocol):
    """Repository interface for managing refresh tokens."""

    def get(self, token: str) -> Token:
        """Get a token by its value.

        Parameters
        ----------
        token
            Token value.

        Returns
        -------
        Token
            Token object with the given token value.
        """
        ...

    def create(self, subject: str) -> Token:
        """Create a new token for a given subject.

        Parameters
        ----------
        subject
            Subject identifier

        Returns
        -------
        Token
            Newly created token object.
        """
        ...

    def delete(self, token: str) -> None:
        """Delete a token by its value.

        Parameters
        ----------
        token
            Token value.
        """
        ...

    def delete_all(self, subject: str) -> None:
        """Delete all tokens for a given subject.

        Parameters
        ----------
        subject
            Subject identifier.
        """
        ...
