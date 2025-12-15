import datetime
from contextlib import suppress

import jsonpatch


class JsonPatch(jsonpatch.JsonPatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_dates()

    def update_dates(self) -> None:
        """Post init to ensure that if a date can be formated to isoformat this
        is done.
        """
        for update in self:
            if isinstance(update['value'], str):
                with suppress(ValueError):
                    update['value'] = datetime.datetime.fromisoformat(
                        update['value']
                    )