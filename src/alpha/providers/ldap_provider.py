from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity

from alpha.connectors.ldap_connector import LDAPConnector


class LDAPProvider:
    protocol = "ldap"

    def __init__(self, connector: LDAPConnector) -> None:
        self.connector = connector

    def authenticate(self, credentials: PasswordCredentials) -> Identity: ...

    def get_user(self, subject: str) -> Identity: ...

    def change_password(self, subject: str, new_password: str) -> None: ...
