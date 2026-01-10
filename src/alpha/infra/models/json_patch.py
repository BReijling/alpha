import datetime
from contextlib import suppress

import jsonpatch


class JsonPatch(jsonpatch.JsonPatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_dates()

    def update_dates(self) -> None:
        """Convert ISO format date strings to datetime objects in the patch"""
        for update in self:
            if isinstance(update['value'], str):
                with suppress(ValueError):
                    update['value'] = datetime.datetime.fromisoformat(
                        update['value']
                    )
