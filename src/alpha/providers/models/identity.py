from dataclasses import dataclass
from typing import Mapping, Any, Sequence
from datetime import datetime


@dataclass(frozen=True)
class Identity:
    subject: str  # unique user id (sub / dn / uid)
    username: str | None
    email: str | None
    display_name: str | None
    groups: Sequence[str]
    claims: Mapping[str, Any]
    issued_at: datetime
    issued_by: str | None
    expires_at: datetime | None
    audience: Sequence[str] | None
    admin: bool = False
    pretend_subject: str | None = None
