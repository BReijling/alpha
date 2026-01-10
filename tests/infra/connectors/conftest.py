import pytest

from ldap3 import MOCK_SYNC
from alpha.infra.connectors.ldap_connector import LDAPConnector


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
