from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity

from alpha.connectors.ldap_connector import LDAPConnector


class LDAPProvider:
    protocol = "ldap"

    def __init__(self, connector: LDAPConnector) -> None:
        self.connector = connector

    def authenticate(
        self, credentials: PasswordCredentials, auto_connect: bool = True
    ) -> Identity:
        if not self.connector.is_connected() and auto_connect:
            self.connector.connect()

        conn = self.connector.get_connection()

        conn.search(
            search_base=self.connector.bind_dn,
            search_filter=f"(uid={credentials.username})",
            attributes=["cn", "mail", "uid"],
        )

        if not conn.entries:
            raise ValueError("User not found")

        entry = conn.entries[0]

        return Identity(
            subject=str(entry.uid),
            username=str(entry.cn),
            display_name=str(entry.cn),
            email=str(entry.mail),
        )

    def get_user(self, subject: str) -> Identity: ...

    def change_password(self, subject: str, new_password: str) -> None: ...
