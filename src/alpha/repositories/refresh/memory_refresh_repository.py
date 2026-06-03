from datetime import datetime, timedelta, timezone

from alpha import exceptions
from alpha.providers.models.token import Token
from alpha.utils.secret_generator import generate_secret


class MemoryRefreshRepository:
    def __init__(
        self,
        token_model: type[Token] = Token,
        token_max_age_seconds: int = 7 * 24 * 3600,
        token_length: int = 32,
    ):
        """Initialize the MemoryRefreshRepository.

        This repository uses an in-memory dictionary to store refresh tokens.
        It provides methods to create, retrieve, delete and delete all refresh
        tokens for a given subject. The tokens are stored in a dictionary where
        the keys are the token values and the values are the token objects.

        Parameters
        ----------
        token_model, optional
            The model class for tokens, by default Token
        token_max_age_seconds, optional
            The maximum age of a token in seconds, by default the equivalent of
            7 days in seconds
        token_length, optional
            The length of the generated token string, by default 32 characters
        """
        self._token_model = token_model
        self._token_max_age_seconds = token_max_age_seconds
        self._token_length = token_length

        self._refresh_tokens: dict[str, Token] = {}

    def get(self, token: str) -> Token:
        """Get a token by its value.

        Parameters
        ----------
        token
            The value of the token to retrieve.

        Returns
        -------
        Token
            The token object corresponding to the given value.

        Raises
        ------
        NotFoundException
            If no token with the given value is found.
        """
        token_object = self._refresh_tokens.get(token, None)
        if not token_object:
            raise exceptions.NotFoundException("Refresh token not found")
        return token_object

    def create(self, subject: str) -> Token:
        """Create a new token for a given subject.

        Parameters
        ----------
        subject
            The subject for which to create a new token.

        Returns
        -------
        Token
            The newly created token object.
        """
        token = self._token_model(
            value=generate_secret(self._token_length),
            token_type="Refresh",
            subject=subject,
            created_at=datetime.now(tz=timezone.utc),
            expires_at=datetime.now(tz=timezone.utc)
            + timedelta(seconds=self._token_max_age_seconds),
        )

        self._refresh_tokens[token.value] = token
        return token

    def delete(self, token: str) -> None:
        """Delete a token by its value.

        Parameters
        ----------
        token
             The value of the token to delete.

        Raises
        ------
        NotFoundException
            If no token with the given value is found.
        """
        if token not in self._refresh_tokens:
            raise exceptions.NotFoundException("Refresh token not found")
        del self._refresh_tokens[token]

    def delete_all(self, subject: str) -> None:
        """Delete all tokens for a given subject.

        Parameters
        ----------
        subject
            The subject for which to delete all tokens.
        """
        tokens_to_delete = [
            token
            for token in self._refresh_tokens
            if self._refresh_tokens[token].subject == subject
        ]

        if not tokens_to_delete:
            return None

        for token in tokens_to_delete:
            del self._refresh_tokens[token]
