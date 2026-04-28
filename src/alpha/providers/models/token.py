from uuid import UUID
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Literal

from alpha.domain.models.base_model import BaseDomainModel


@dataclass
class Token(BaseDomainModel):
    """Represents an authentication token.

    Attributes
    ----------
    value
        The token value, typically a JWT or opaque string.
    token_type
        The type of token, e.g. "Bearer" or "Refresh".
    subject
        The subject or user associated with the token.
    id
        Optional unique identifier for the token.
    created_at
        Optional timestamp when the token was created.
    expires_at
        Optional timestamp when the token expires.
    """

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
        """Creates a Token instance from a dictionary.

        Parameters
        ----------
        data
            A dictionary containing the token data. Expected keys include:

            - "id": Optional string representation of a UUID.
            - "value": The token value (required).
            - "subject": Optional subject or user associated with the token.
            - "token_type": Optional token type, defaults to "Bearer".
            - "created_at": Optional ISO format datetime string for when the
            token was created.
            - "expires_at": Optional ISO format datetime string for when the
            token expires.

        Returns
        -------
        Token
            A Token instance created from the provided dictionary.
        """
        return cls(
            id=UUID(data["id"]) if data.get("id") else None,
            value=data["value"],
            subject=data.get("subject"),
            token_type=data.get("token_type", "Bearer"),
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
        """Converts the Token instance to a dictionary.

        Returns
        -------
        dict[str, str | None]
            A dictionary representation of the Token instance with the
            following keys:

            - "id": String representation of the UUID or None.
            - "value": The token value.
            - "subject": The subject or user associated with the token.
            - "token_type": The type of token.
            - "created_at": ISO format datetime string for when the token was
            created or None.
            - "expires_at": ISO format datetime string for when the token
            expires or None.
        """
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
