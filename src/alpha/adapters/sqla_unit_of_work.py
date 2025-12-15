"""Contains the SQLAlchemy Unit of Work implementation."""

from typing import Any, TypeVar

from sqlalchemy.orm.session import Session

from alpha import exceptions
from alpha.interfaces.sql_database import SqlDatabase
from alpha.repositories.models.repository_model import RepositoryModel

UOW = TypeVar("UOW", bound="SqlAlchemyUnitOfWork")


class SqlAlchemyUnitOfWork:
    """Unit of Work implementation for SQLAlchemy databases."""

    def __init__(self, db: SqlDatabase, repos: list[RepositoryModel]) -> None:
        """Initialize the Unit of Work with a database and repositories.

        Parameters
        ----------
        db : SqlDatabase
            The database instance to use.
        repos : list[RepositoryModel]
            The list of repository models to use.

        Raises
        ------
        TypeError
            If the provided database is not a valid SqlDatabase instance.
        TypeError
            If the provided repositories list is empty or contains invalid
            models.
        """
        if not isinstance(db, SqlDatabase):  # type: ignore
            raise TypeError("No valid database provided")

        self._db = db
        self._repositories = repos
        self._session: Session | None = None

    def __enter__(self: UOW) -> UOW:
        """Initialize the Unit of Work context.

        Returns
        -------
            The Unit of Work instance.

        Raises
        ------
        TypeError
            If the provided repositories list is empty or contains invalid
            models.
        """
        self._session = self._db.get_session()

        for repo in self._repositories:
            session = self._session
            model = repo.default_model

            name: str = repo.name
            repository = repo.repository
            interface: Any = repo.interface

            self.__setattr__(
                name,
                repository(session=session, default_model=model),  # type: ignore
            )
            if interface:
                if not isinstance(getattr(self, name), interface):
                    raise TypeError(f"Repository for {name} has no interface")

        return self

    def __exit__(self, *args: Any) -> None:
        """Finalize the Unit of Work context."""
        if not self._session:
            raise exceptions.DatabaseSessionError(
                "No active database session is defined"
            )
        self._session.close()
        self.rollback()
        self._session = None  # type: ignore

    def commit(self) -> None:
        """Commit the current transaction."""
        if not self._session:
            raise exceptions.DatabaseSessionError(
                "No active database session is defined"
            )
        self._session.commit()

    def flush(self) -> None:
        """Flush the current transaction."""
        if not self._session:
            raise exceptions.DatabaseSessionError(
                "No active database session is defined"
            )
        self._session.flush()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        if not self._session:
            raise exceptions.DatabaseSessionError(
                "No active database session is defined"
            )
        self._session.rollback()

    def refresh(self, obj: object) -> None:
        """Refresh the state of a given object."""
        if not self._session:
            raise exceptions.DatabaseSessionError(
                "No active database session is defined"
            )
        self._session.refresh(obj)

    @property
    def session(self) -> Session | None:
        """Get the current database session."""
        return self._session
