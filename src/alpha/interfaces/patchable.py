from typing import Protocol, Sequence

from alpha.domain.models.base_model import DomainModelCovariant
from alpha.infra.models.json_patch import JsonPatch, PatchDict


class Patchable(Protocol[DomainModelCovariant]):
    """Protocol for patchable domain models."""

    @property
    def __patch_fields__(self) -> Sequence[str]:
        """List of fields that can be patched."""
        ...

    def patch(
        self, patches: PatchDict | list[PatchDict] | JsonPatch
    ) -> DomainModelCovariant:
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
