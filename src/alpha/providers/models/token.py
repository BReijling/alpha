from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    value: str
    token_type: str = "Bearer"
