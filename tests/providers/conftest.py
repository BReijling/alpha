import pytest

from alpha.providers.ldap_provider import LDAPProvider, ADProvider
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import DEFAULT_LDAP_MAPPINGS


class FakeLDAPEntry:
    def __init__(self, dn: str, attributes: dict[str, str | list[str]]):
        self.dn = dn
        self.entry_dn = dn
        self.entry_attributes = attributes

    @property
    def entry_attributes_as_dict(self):
        return self.entry_attributes


class FakeLDAPServer:
    def __init__(self, host: str):
        self.host = host


class FakeLDAPConnection:
    def __init__(self, server: str, user: str, password: str, *args, **kwargs):
        self.server = FakeLDAPServer(server)

        self.entries = []

    def bind(self):
        # Simulate a successful bind operation
        return True

    def search(self, search_base, search_filter, *args, **kwargs):
        # Simulate a search operation returning a mock entry
        if "ldap_user" in search_filter:
            self.entries = [
                FakeLDAPEntry(
                    dn=f"cn=ldap_user,{search_base}",
                    attributes={
                        "uid": "ldap_user",
                        "cn": "LDAP User",
                        "mail": "ldap_user@example.com",
                        "memberOf": [
                            "cn=group1,dc=example,dc=com",
                            "cn=group2,dc=example,dc=com",
                        ],
                    },
                )
            ]
        elif "ad_user" in search_filter:
            self.entries = [
                FakeLDAPEntry(
                    dn=f"cn=ad_user,{search_base}",
                    attributes={
                        "sAMAccountName": "ad_user",
                        "cn": "AD User",
                        "displayName": "AD User",
                        "mail": "ad_user@example.com",
                        "memberOf": [
                            "cn=group1,dc=example,dc=com",
                            "cn=group2,dc=example,dc=com",
                        ],
                    },
                )
            ]
        else:
            self.entries = []


class FakeLDAPConnector:
    def __init__(self):
        self._connection = None
        self._client_strategy = None

    def connect(self, server_host: str, user_dn: str, password: str):
        # Simulate a connection to the LDAP server
        self._connection = FakeLDAPConnection(server_host, user_dn, password)

    def get_connection(self):
        return self._connection

    def is_connected(self):
        return self._connection is not None

    def get_server(self):
        return "fake"

    @property
    def connection_cls(self):
        return FakeLDAPConnection


@pytest.fixture
def search_base():
    return "ou=users,dc=example,dc=com"


@pytest.fixture
def ldap_connector(search_base):
    connector = FakeLDAPConnector()
    connector.connect(
        server_host="fake_ldap_server",
        user_dn=f"cn=ad_user,{search_base}",
        password="fake_password",
    )
    return connector


@pytest.fixture
def ldap_provider(ldap_connector, search_base):

    provider = LDAPProvider(
        connector=ldap_connector,
        search_filter_key="uid",
        search_base=search_base,
        search_attributes=["uid", "cn", "mail", "memberOf"],
        auto_connect=True,
        change_password_supported=True,
    )
    return provider


@pytest.fixture
def ad_provider(ldap_connector, search_base):

    provider = ADProvider(
        connector=ldap_connector,
        search_filter_key="uid",
        search_base=search_base,
        search_attributes=["uid", "cn", "mail", "memberOf"],
        identity_mappings=DEFAULT_LDAP_MAPPINGS,
        auto_connect=True,
        change_password_supported=True,
    )
    return provider


@pytest.fixture
def ldap_provider_no_auto_connect(ldap_connector, search_base):

    provider = LDAPProvider(
        connector=ldap_connector,
        search_filter_key="uid",
        search_base=search_base,
        search_attributes=["uid", "cn", "mail"],
        auto_connect=False,
        change_password_supported=False,
    )
    return provider


@pytest.fixture
def credentials():
    return PasswordCredentials(username="ldap_user", password="test_password")
