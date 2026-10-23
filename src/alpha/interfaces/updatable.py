from typing import Protocol, Sequence

from alpha.domain.models.base_model import (
    DomainModelCovariant,
    BaseDomainModel,
)


class Updatable(Protocol[DomainModelCovariant]):
    """Updatable interface for updating domain models."""

    @property
    def __update_fields__(self) -> Sequence[str]:
        """List of fields that can be updated."""
        ...

    def update(self, obj: BaseDomainModel) -> DomainModelCovariant:
        """Update a domain model object.

        Parameters
        ----------
        obj
            The domain model object to be updated.

        Returns
        -------
            The updated domain model object.
        """
        ...
