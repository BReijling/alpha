from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity


class LDAPProvider:
    def authenticate(self, credentials: PasswordCredentials) -> Identity: ...

    def get_user(self, subject: str) -> Identity: ...

    def change_password(self, subject: str, new_password: str) -> None: ...
