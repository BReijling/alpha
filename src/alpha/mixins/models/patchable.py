from datetime import UTC, datetime
from typing import Literal, Self


class PatchableMixin:
    """This mixin class provides patching capabilities for model instances.

    The subclass must define the `__patch_fields__` attribute or property,
    which should be a list of field names that are allowed to be patched.

    Example
    -------
    class MyModel(BaseDomainModel, PatchableMixin):
        __patch_fields__ = ["name", "description"]
    """

    @property
    def __patch_fields__(self) -> list[str]:
        raise NotImplementedError(
            "Subclasses must implement the __patch_fields__ property."
        )

    def patch(
        self,
        patch: dict[Literal["op", "path", "value"], str],
    ) -> Self:
        """Patch the current instance with the given patch dictionary. In order
        to be patchable, the field must be listed in the __patch_fields__
        attribute or property.

        Parameters
        ----------
        patch
            A dictionary representing the patch operation. It should contain
            the keys "op", "path", and "value".

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
        op = patch.get("op")
        path = str(patch.get("path")).strip("/")
        value = patch.get("value")

        if path not in self.__patch_fields__:
            raise ValueError(f"Field '{path}' cannot be patched.")

        if op == "replace":
            setattr(self, path, value)
        elif op == "add":
            if isinstance(getattr(self, path), (list | tuple)):
                getattr(self, path).append(value)
            else:
                setattr(self, path, value)
        elif op == "remove":
            if isinstance(getattr(self, path), (list | tuple)):
                getattr(self, path).remove(value)
            else:
                setattr(self, path, None)
        else:
            raise ValueError(f"Unsupported patch operation '{op}'.")

        if hasattr(self, "modified_at"):
            setattr(self, "modified_at", datetime.now(tz=UTC))
        if hasattr(self, "updated_at"):
            setattr(self, "updated_at", datetime.now(tz=UTC))
        return self
