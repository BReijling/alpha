"""Contains the UnitOfWork protocol, which defines the interface for a unit of
work implementation.
"""

from typing import (
    Any,
    Protocol,
    TypeVar,
    runtime_checkable,
)

UOW = TypeVar("UOW", bound="UnitOfWork", covariant=True)
"""A covariant TypeVar bound to UnitOfWork.

This is used to represent the `Self` type for subclasses of `UnitOfWork`,
allowing static type checkers to correctly infer the specific subclass
instance within a `with` statement context.
"""


@runtime_checkable
class UnitOfWork(Protocol[UOW]):
    """Unit of Work protocol defining the interface for a unit of work
    implementation.
    """

    def __enter__(self) -> UOW:
        """Enter the runtime context related to this object.

        Returns
        -------
        UOW
            The unit of work instance.
        """
        ...

    def __exit__(self, *args: Any) -> None:
        """Exit the runtime context related to this object."""
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
