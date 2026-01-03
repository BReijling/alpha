from ldap3 import Server, Connection, Tls, ALL
import ssl


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
        """
        self.server_url = server_url
        self.bind_dn = bind_dn
        self.bind_password = bind_password

        tls = None
        if use_tls:
            tls = Tls(
                validate=ssl.CERT_REQUIRED,
                version=ssl.PROTOCOL_TLSv1_2,
            )

        self.server = Server(
            host=self.server_url,
            port=server_port,
            use_ssl=use_tls,
            tls=tls,
            get_info=ALL,
        )

    def connect(self) -> None:
        """Method to establish a connection to the LDAP server."""
        self.connection = Connection(
            self.server,
            user=self.bind_dn,
            password=self.bind_password,
            auto_bind=True,
        )

    def disconnect(self) -> None:
        """Method to close the connection to the LDAP server."""
        self.connection.unbind()
