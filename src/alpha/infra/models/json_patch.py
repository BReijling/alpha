import datetime
from contextlib import suppress

import jsonpatch  # type: ignore[import-untyped]


class JsonPatch(jsonpatch.JsonPatch):
    """A JSON Patch that automatically converts ISO format date strings to
    datetime objects.

    This class extends the standard JsonPatch to include functionality for
    converting date strings in the patch operations to datetime objects. This
    is useful for ensuring that any date values in the patch are properly
    handled as datetime objects.
    """

    def __init__(self, patch: list[dict[str, str]], *args, **kwargs):
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
        super().__init__(patch=patch, *args, **kwargs)
        self.update_dates()

    def update_dates(self) -> None:
        """Convert ISO format date strings to datetime objects in the patch"""
        for update in self:
            if isinstance(update["value"], str):
                with suppress(ValueError):
                    update["value"] = datetime.datetime.fromisoformat(
                        update["value"]
                    )
