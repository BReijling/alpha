from datetime import datetime, date
from contextlib import suppress
from typing import Any, Literal

import jsonpatch  # type: ignore[import-untyped]


PatchOp = Literal["replace", "add", "remove"]
PatchDict = dict[Literal["op", "path", "value"], Any]


class JsonPatch(jsonpatch.JsonPatch):
    """A JSON Patch that automatically converts ISO format date and datetime
    strings to date and datetime objects.

    This class extends the standard JsonPatch to include functionality for
    converting date and datetime strings in the patch operations to date or
    datetime objects. This is useful for ensuring that any date values in the
    patch are properly handled as datetime objects.
    """

    def __init__(self, patch: list[PatchDict], *args: Any, **kwargs: Any):
        """Initialize the JsonPatch. This method calls the parent class's
        initializer and then updates the date values in the patch operations.

        Parameters
        ----------
        patch
            A list of JSON Patch operations, where each operation is a
            dictionary containing the operation type, path, and value. The
            value can be a string in ISO format representing a date, which will
            be converted to a datetime object.
        *args
            Additional positional arguments to be passed to the parent class's
            initializer.
        **kwargs
            Additional keyword arguments to be passed to the parent class's
            initializer.
        """
        self.patch: list[PatchDict] = patch
        super().__init__(patch=patch, *args, **kwargs)
        self.parse_dates()
        self.parse_booleans()

    def parse_dates(self) -> None:
        """Convert ISO format date strings to datetime objects in the patch"""
        for patch in self.patch:
            value = patch.get("value", None)
            if not isinstance(value, str):
                continue
            if value:
                # Try to parse the value as a date first, then as a datetime
                with suppress(ValueError):
                    patch["value"] = date.fromisoformat(value)
                    continue
                with suppress(ValueError):
                    patch["value"] = datetime.fromisoformat(value)

    def parse_booleans(self) -> None:
        """Convert string representations of booleans to actual boolean objects
        in the patch
        """
        for patch in self.patch:
            value = patch.get("value", None)
            if isinstance(value, str):
                if value.lower() == "true":
                    patch["value"] = True
                elif value.lower() == "false":
                    patch["value"] = False
