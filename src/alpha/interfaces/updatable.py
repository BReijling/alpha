from typing import Protocol

from alpha.domain.models.base_model import DomainModel


class Updatable(Protocol):
    """Updatable interface for updating domain models."""

    def update(self, obj: DomainModel) -> DomainModel:
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
