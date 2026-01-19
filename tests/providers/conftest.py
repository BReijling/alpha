from typing import Any
import pytest

from alpha.infra.connectors.oidc_connector import OIDCConnector
from alpha.providers.ldap_provider import LDAPProvider, ADProvider
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.token import Token
from alpha.providers.oidc_provider import OIDCProvider
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

    def unbind(self):
        # Simulate an unbind operation
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


class FakeOIDCConnector:
    def __init__(self):
        self._introspection_url = "https://example.com/introspect"
        self._client_id = "fake_client_id"
        self._client_secret = "fake_client_secret"
        self._scope = "openid profile email"
        self.userinfo_url = "https://example.com/userinfo"
        self.introspection_url = "https://example.com/introspect"
        self.user_lookup_url_template = "test/users/{user_id}"

    def request_password_token(self, *args, **kwargs) -> dict[str, Any]:
        return {
            "access_token": "fake_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": self._scope,
        }

    def request_client_credentials_token(self) -> dict[str, Any]:
        return {
            "access_token": "fake_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": self._scope,
        }

    def get_userinfo(self, access_token: str) -> dict[str, Any]:
        return {
            "sub": "oidc_user",
            "name": "OIDC User",
            "preferred_username": "oidc_user",
            "email": "oidc_user@example.com",
        }

    def introspect_token(self, token: str) -> dict[str, Any]:
        return {
            "active": True,
            "scope": self._scope,
            "client_id": self._client_id,
            "username": "oidc_user",
            "token_type": "Bearer",
            "exp": 9999999999,
            "iat": 1111111111,
            "nbf": 1111111111,
            "sub": "oidc_user",
            "aud": self._client_id,
            "iss": "https://example.com",
            "jti": "unique-token-id",
        }

    def get_user_by_subject(self, subject: str) -> dict[str, Any]:
        return {
            "sub": subject,
            "name": "OIDC User",
            "preferred_username": "oidc_user",
            "email": "oidc_user@example.com",
        }


@pytest.fixture
def search_base():
    return "ou=users,dc=example,dc=com"


@pytest.fixture
def fake_ldap_connector(search_base):
    connector = FakeLDAPConnector()
    connector.connect(
        server_host="fake_ldap_server",
        user_dn=f"cn=ad_user,{search_base}",
        password="fake_password",
    )
    return connector


@pytest.fixture
def ldap_provider(fake_ldap_connector, search_base):

    provider = LDAPProvider(
        connector=fake_ldap_connector,
        search_filter_key="uid",
        search_base=search_base,
        search_attributes=["uid", "cn", "mail", "memberOf"],
        auto_connect=True,
        change_password_supported=True,
    )
    return provider


@pytest.fixture
def ad_provider(fake_ldap_connector, search_base):

    provider = ADProvider(
        connector=fake_ldap_connector,
        search_filter_key="uid",
        search_base=search_base,
        search_attributes=["uid", "cn", "mail", "memberOf"],
        identity_mappings=DEFAULT_LDAP_MAPPINGS,
        auto_connect=True,
        change_password_supported=True,
    )
    return provider


@pytest.fixture
def ldap_provider_no_auto_connect(fake_ldap_connector, search_base):

    provider = LDAPProvider(
        connector=fake_ldap_connector,
        search_filter_key="uid",
        search_base=search_base,
        search_attributes=["uid", "cn", "mail"],
        auto_connect=False,
        change_password_supported=False,
    )
    return provider


@pytest.fixture
def ldap_credentials():
    return PasswordCredentials(username="ldap_user", password="test_password")


@pytest.fixture
def fake_oidc_connector():
    connector = FakeOIDCConnector()
    return connector


@pytest.fixture
def oidc_provider(fake_oidc_connector: OIDCConnector):
    provider = OIDCProvider(connector=fake_oidc_connector)
    return provider


@pytest.fixture
def credentials():
    return PasswordCredentials(username="test_user", password="test_password")


@pytest.fixture
def token():
    return Token("fake_access_token")
