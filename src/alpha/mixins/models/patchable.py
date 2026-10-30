from datetime import UTC, datetime
from typing import Self, Sequence, MutableSequence

from alpha.infra.models.json_patch import JsonPatch, PatchDict


class PatchableMixin:
    """This mixin class provides patching capabilities for model instances.

    The subclass must define the `__patch_fields__` attribute or property,
    which should be a list of field names that are allowed to be patched.

    Example
    -------
    ```python
    class MyModel(BaseDomainModel, PatchableMixin):
        __patch_fields__ = ["name", "description"]
    ```
    """

    @property
    def __patch_fields__(self) -> Sequence[str]:
        raise NotImplementedError(
            "Subclasses must implement the __patch_fields__ property."
        )

    def patch(
        self,
        patches: PatchDict | list[PatchDict] | JsonPatch,
    ) -> Self:
        """Patch the current instance with the given patch dictionary. In order
        to be patchable, the field must be listed in the __patch_fields__
        attribute or property.

        In case the instance has attributes like "modified_at" or "updated_at",
        they will be updated to the current UTC time after applying the patch.

        Parameters
        ----------
        patches
            A dictionary representing the patch operation, a list of such
            dictionaries, or a JsonPatch instance. Each dictionary should
            contain the keys "op", "path", and "value".

        Returns
        -------
            The patched instance of the current object.

        Raises
        ------
        ValueError
            If the specified field cannot be patched.
        ValueError
            If the patch operation is unsupported.
        """
        if isinstance(patches, JsonPatch):
            for single_patch in patches.patch:
                self._apply_patch(single_patch)
        elif isinstance(patches, list):
            for single_patch in patches:
                self._apply_patch(single_patch)
        else:
            self._apply_patch(patches)

        if hasattr(self, "modified_at"):
            setattr(self, "modified_at", datetime.now(tz=UTC))
        if hasattr(self, "updated_at"):
            setattr(self, "updated_at", datetime.now(tz=UTC))
        return self

    def _apply_patch(self, patch: PatchDict) -> None:
        """Apply a patch to the current instance.

        Parameters
        ----------
        patch
            A dictionary representing the patch operation. It should contain
            the keys "op", "path", and "value".
        """
        op = patch.get("op")
        path = str(patch.get("path")).strip("/").replace("/", ".")
        if op in ("add", "replace") and "value" not in patch:
            raise ValueError(
                f"Patch operation '{op}' for field '{path}' requires a value."
            )
        value = patch.get("value")

        if path not in self.__patch_fields__:
            raise ValueError(f"Field '{path}' cannot be patched.")

        if op == "replace":
            setattr(self, path, value)
        elif op == "add":
            if isinstance(getattr(self, path), MutableSequence):
                getattr(self, path).append(value)
            else:
                setattr(self, path, value)
        elif op == "remove":
            if isinstance(getattr(self, path), MutableSequence):
                getattr(self, path).remove(value)
            else:
                setattr(self, path, None)
        else:
            raise ValueError(f"Unsupported patch operation '{op}'.")
