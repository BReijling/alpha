from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordCredentials:
    username: str
    password: str
