from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token


class KeycloakProvider:
    protocol = "oauth2"

    def __init__(self) -> None:
        pass

    def authenticate(self, credentials: PasswordCredentials) -> Identity: ...

    def get_user(self, subject: str) -> Identity: ...

    def validate(self, token: Token) -> Identity: ...
