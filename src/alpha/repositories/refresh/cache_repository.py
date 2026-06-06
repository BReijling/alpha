from typing import Any

from alpha.providers.models.token import Token


class CacheRefreshRepository:
    def __init__(
        self,
        cache_connector: Any,
        token_model: type[Token] = Token,
        token_max_age_seconds: int = 7 * 24 * 3600,
        token_length: int = 32,
    ):
        """Initialize the CacheRefreshRepository with the given cache connector.

        *** This class is not fully implemented yet. The methods are defined
        but not implemented. ***

        Parameters
        ----------
        cache_connector
            The cache connector instance to use for cache operations.
        token_model
            The model class for tokens, by default Token. The model class
            should have a `from_dict` class method that takes a dictionary and
            returns an instance of the model. The dictionary will have the same
            structure as the token data in the JSON file. The model class
            should also have a `to_dict` method that converts an instance of
            the model to a dictionary with the same structure as the token data
            in the JSON file. The model class should also have a
            `create_refresh` class method that creates a new refresh token.
        token_max_age_seconds
            The maximum age of a token in seconds, by default the equivalent of
            7 days in seconds
        token_length
            The length of the generated token string, by default 32 characters
        """
        self._cache_connector = cache_connector
        self._token_model = token_model
        self._token_max_age_seconds = token_max_age_seconds
        self._token_length = token_length

    def get(self, token: str) -> Token:
        """Get a token by its value."""
        raise NotImplementedError("Method not implemented yet.")

    def create(self, subject: str) -> Token:
        """Create a new token for a given subject."""
        raise NotImplementedError("Method not implemented yet.")

    def delete(self, token: str) -> None:
        """Delete a token by its value."""
        raise NotImplementedError("Method not implemented yet.")

    def delete_all(self, subject: str) -> None:
        """Delete all tokens for a given subject."""
        raise NotImplementedError("Method not implemented yet.")
