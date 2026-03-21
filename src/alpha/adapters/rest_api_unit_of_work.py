"""Contains the REST API Unit of Work implementation."""

from typing import Any, TypeVar

import requests

from alpha.repositories.models.repository_model import RepositoryModel


UOW = TypeVar("UOW", bound="RestApiUnitOfWork")


class RestApiUnitOfWork:
    """Unit of Work implementation for REST API interactions."""

    def __init__(
        self,
        repos: list[RepositoryModel],
        session: requests.sessions.Session | None = None,
    ) -> None:
        """Initialize the Unit of Work with repositories.

        Parameters
        ----------
        repos : list[RepositoryModel]
            The list of repository models to use.
        session : requests.sessions.Session | None
            The session to use for API interactions.

        Raises
        ------
        TypeError
            If the provided repositories list is empty or contains invalid
            models.
        """
        self._repositories = repos
        self._session = session

    def __enter__(self: UOW) -> UOW:
        """_summary_"""
        self._session = self._session or requests.sessions.Session()

        for repo in self._repositories:
            name: str = repo.name
            interface: Any = repo.interface
            additional_config: dict[str, Any] | None = (
                repo.additional_config or {}
            )

            self.__setattr__(
                name,
                repo.repository(
                    session=self._session,
                    default_model=repo.default_model,
                    **additional_config,
                ),
            )

            if interface:
                if not isinstance(getattr(self, name), interface):
                    raise TypeError(f"Repository for {name} has no interface")

        return self

    def __exit__(self, *args: Any) -> None:
        """Finalize the Unit of Work context."""
        if self._session:
            self._session.close()

    def commit(self) -> None:
        raise NotImplementedError("RestApiUnitOfWork does not support commit")

    def flush(self) -> None:
        raise NotImplementedError("RestApiUnitOfWork does not support flush")

    def rollback(self) -> None:
        raise NotImplementedError(
            "RestApiUnitOfWork does not support rollback"
        )

    def refresh(self, obj: object) -> None:
        raise NotImplementedError("RestApiUnitOfWork does not support refresh")

    @property
    def session(self) -> requests.sessions.Session | None:
        """Get the current session.

        Returns
        -------
        requests.sessions.Session | None
            The current session used for API interactions.
        """
        return self._session
