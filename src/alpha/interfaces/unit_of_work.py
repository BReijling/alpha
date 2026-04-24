"""Contains the UnitOfWork protocol, which defines the interface for a unit of
work implementation.
"""

from typing import (
    Any,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from sqlalchemy.orm.session import Session

UOW = TypeVar("UOW", bound="UnitOfWork")


@runtime_checkable
class UnitOfWork(Protocol):
    """Unit of Work protocol defining the interface for a unit of work 
    implementation.
    """

    def __enter__(self: UOW) -> UOW:
        """Enter the runtime context related to this object.

        Returns
        -------
        UOW
            The unit of work instance.
        """
        ...

    def __exit__(self, *args: Any) -> None:
        """Exit the runtime context related to this object.
        """
        ...

    def commit(self) -> None:
        """Commit the current transaction."""
        ...

    def flush(self) -> None:
        """Flush the current session."""
        ...

    def rollback(self) -> None:
        """Rollback the current transaction."""
        ...

    def refresh(self, obj: object) -> None:
        """Refresh the state of the given object from the database.
        
        Parameters
        ----------
        obj
            The object to refresh.
        """
        ...

    @property
    def session(self) -> Session:
        """Get the current session.

        Returns
        -------
        Session
            The current SQLAlchemy session.
        """
        ...
        