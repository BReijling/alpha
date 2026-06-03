from typing import Any

from alpha.providers.models.token import Token


class CacheRefreshRepository:
    def __init__(self, cache_connector: Any):
        self.cache_connector = cache_connector

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
