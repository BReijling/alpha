from dataclasses import dataclass
from datetime import datetime


@dataclass
class LifeCycleBase:
    created_by: str | None = None
    created_at: datetime | None = None
    modified_by: str | None = None
    modified_at: datetime | None = None
