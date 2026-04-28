from dataclasses import dataclass
from datetime import datetime


@dataclass
class LifeCycleBase:
    """Base class for lifecycle model attributes which can be inherited by all
    domain models in the application.

    Attributes
    ----------
    created_by
        The identifier of the user who created the instance. This can be a
        string or None.
    created_at
        The timestamp when the instance was created. This can be a datetime
        object or None.
    modified_by
        The identifier of the user who last modified the instance. This can be
        a string or None.
    modified_at
        The timestamp when the instance was last modified. This can be a
        datetime object or None.
    """

    created_by: str | None = None
    created_at: datetime | None = None
    modified_by: str | None = None
    modified_at: datetime | None = None
