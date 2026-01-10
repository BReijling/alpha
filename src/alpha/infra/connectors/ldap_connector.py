from ldap3 import Server, Connection, Tls, ALL, SYNC
import ssl
from typing import Any, Literal, cast

ClientStrategyType = Literal[
    'SYNC',
    'SAFE_RESTARTABLE',
    'SAFE_SYNC',
    'ASYNC',
    'LDIF',
    'RESTARTABLE',
    'REUSABLE',
    'MOCK_SYNC',
    'MOCK_ASYNC',
    'ASYNC_STREAM',
]


class LDAPConnector:
    """LDAP connector.

    Intended for providers that connect to LDAP directories.

    For example, connecting to an LDAP server to authenticate users
    or retrieve user information.
    """

    def __init__(
        self,
        server_url: str,
        bind_dn: str,
        bind_password: str,
        server_port: int = 636,
        use_tls: bool = True,
        client_strategy: ClientStrategyType = SYNC,
    ) -> None:
        """Initialize the LDAP connector with server details.

        Parameters
        ----------
        server_url
            URL of the LDAP server.
        bind_dn
            Distinguished Name (DN) for binding to the LDAP server.
        bind_password
            Password for the bind DN.
        use_tls
            Whether to use TLS for the connection.
        server_port
            Port of the LDAP server.
        client_strategy
            The client strategy to use for the connection.
        """
        self._server_url = server_url
        self._bind_dn = bind_dn
        self._bind_password = bind_password
        self._client_strategy = client_strategy

        tls = None
        if use_tls:
            tls = Tls(
                validate=ssl.CERT_REQUIRED,
                version=ssl.PROTOCOL_TLSv1_2,
            )

        self._server = Server(
            host=self._server_url,
            port=server_port,
            use_ssl=use_tls,
            tls=tls,
            get_info=ALL,
        )
        self._connection: Connection | None = None

    def connect(self) -> None:
        """Method to establish a connection to the LDAP server."""
        self._connection = self.connection_cls(
            self._server,
            user=self._bind_dn,
            password=self._bind_password,
            auto_bind=True,
            client_strategy=self._client_strategy,  # type: ignore
        )

    def disconnect(self) -> None:
        """Method to close the connection to the LDAP server."""
        if self.is_connected():
            cast(Any, self._connection).unbind()
        self._connection = None

    def is_connected(self) -> bool:
        """Check if the connection to the LDAP server is active."""
        return self._connection is not None and self._connection.bound

    def get_connection(self) -> Connection:
        """Get the current LDAP connection.

        Returns
        -------
        Connection
            The active LDAP connection.

        Raises
        ------
        RuntimeError
            If the connection is not established.
        """
        if not self._connection or not self.is_connected():
            raise RuntimeError("LDAP connection is not established.")
        return self._connection

    def get_server(self) -> Server:
        """Get the LDAP server."""
        return self._server

    @property
    def connection_cls(self) -> type[Connection]:
        """Get the connection class."""
        return Connection

    @property
    def bind_dn(self) -> str:
        """Get the bind DN."""
        return self._bind_dn
