from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    value: str
    token_type: str = "Bearer"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Token(value='{self.value}', token_type='{self.token_type}')"
