from uuid import UUID
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Literal

from alpha.domain.models.base_model import BaseDomainModel


@dataclass
class Token(BaseDomainModel):
    value: str
    token_type: Literal["Bearer", "Refresh"] = "Bearer"
    subject: str | None = None
    id: UUID | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Token(value='<redacted>', token_type='{self.token_type}')"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Token":
        return cls(
            id=UUID(data["id"]) if data.get("id") else None,
            value=data["value"],
            subject=data.get("subject"),
            token_type=data.get("token_type", "Refresh"),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
        )

    def to_dict(self) -> dict[str, str | None]:
        return {
            "id": str(self.id) if self.id else None,
            "value": self.value,
            "subject": self.subject,
            "token_type": self.token_type,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "expires_at": (
                self.expires_at.isoformat() if self.expires_at else None
            ),
        }
