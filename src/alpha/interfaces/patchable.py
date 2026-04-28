from typing import Protocol

from alpha.domain.models.base_model import DomainModelCovariant
from alpha.infra.models.json_patch import JsonPatch


class Patchable(Protocol[DomainModelCovariant]):
    """Protocol for patchable domain models."""

    def patch(self, patches: JsonPatch) -> DomainModelCovariant:
        """Patch the domain model instance with the given JSON Patch.

        Parameters
        ----------
        patches
            A JsonPatch object containing the patches to be applied to the
            domain model instance.

        Returns
        -------
        DomainModelCovariant
            The updated domain model instance after applying the patches.
        """
        ...
