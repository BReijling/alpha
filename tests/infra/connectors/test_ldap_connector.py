from ldap3 import SYNC, MOCK_SYNC, Connection
from alpha.infra.connectors.ldap_connector import (
    LDAPConnector,
)


def test_ldap_connector_initialization():
    connector = LDAPConnector(
        server_url="ldap.example.com",
        bind_dn="cn=admin,dc=example,dc=com",
        bind_password="password",
    )

    assert connector._server_url == "ldap.example.com"
    assert connector._bind_dn == "cn=admin,dc=example,dc=com"
    assert connector._bind_password == "password"
    assert connector._client_strategy == SYNC
    assert connector.connection_cls == Connection


def test_ldap_connector_connect(ldap_connector):
    ldap = ldap_connector

    assert ldap._connection is None
    assert not ldap.is_connected()

    ldap.connect()
    assert ldap._connection is not None


def test_ldap_connector_connection_properties(ldap_connector):
    ldap = ldap_connector
    ldap.connect()

    assert ldap._server.host == "fake"
    assert ldap.bind_dn == "cn=admin,dc=example,dc=com"

    conn = ldap._connection

    assert conn.server.host == "fake"
    assert conn.server.port == 636
    assert conn.server.ssl is False
    assert conn.strategy_type == MOCK_SYNC
