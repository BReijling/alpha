"""_summary_
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
    """_summary_

    Parameters
    ----------
    Protocol : _type_
        _description_
    """

    def __enter__(self: UOW) -> UOW:
        """_summary_"""
        ...

    def __exit__(self, *args: Any) -> None:
        """_summary_"""

    def commit(self) -> None:
        """_summary_"""

    def flush(self) -> None:
        """_summary_"""

    def rollback(self) -> None:
        """_summary_"""

    def refresh(self, obj: object) -> None:
        """_summary_"""

    @property
    def session(self) -> Session:
        """_summary_

        Returns
        -------
        Session
            _description_
        """
