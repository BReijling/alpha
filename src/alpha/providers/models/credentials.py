from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordCredentials:
    username: str
    password: str

    def to_dict(self) -> dict[str, str]:
        return {"username": self.username, "password": self.password}

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return (
            "PasswordCredentials("
            f"username={self.username!r}, "
            "password=***"
            ")"
        )
