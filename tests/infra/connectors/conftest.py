import pytest

from ldap3 import MOCK_SYNC
from alpha.infra.connectors.ldap_connector import LDAPConnector
from alpha.infra.connectors.oidc_connector import OIDCConnector


@pytest.fixture
def ldap_connector():
    connector = LDAPConnector(
        server_url="fake",
        bind_dn="cn=admin,dc=example,dc=com",
        bind_password="password",
        server_port=636,
        use_tls=False,
        client_strategy=MOCK_SYNC,
    )
    return connector


@pytest.fixture
def oidc_connector():
    connector = OIDCConnector(
        base_url="https://example.com",
        token_url="token",
        userinfo_url=None,
        introspection_url="https://example.com/introspect",
        client_id="fake_client_id",
        client_secret="fake_client_secret",
        scope=["openid", "profile", "email"],
        user_lookup_url_template="test/users/{user_id}",
    )
    return connector


@pytest.fixture
def fake_response():
    class FakeResponse:
        def __init__(self, status_code: int, json_data: dict):
            self.status_code = status_code
            self._json_data = json_data

        def json(self):
            return self._json_data

    return FakeResponse
