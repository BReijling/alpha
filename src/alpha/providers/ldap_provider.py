"""LDAP Identity Provider Module"""

from typing import Any, cast

from ldap3 import Connection, ALL_ATTRIBUTES
from ldap3.abstract.entry import Entry
from ldap3.core.exceptions import LDAPException

from alpha.infra.connectors.ldap_connector import LDAPConnector
from alpha.interfaces.token_factory import TokenFactory
from alpha.mixins.jwt_provider import JWTProviderMixin
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import (
    DEFAULT_LDAP_MAPPINGS,
    DEFAULT_AD_MAPPINGS,
    AD_SEARCH_ATTRIBUTES,
    Identity,
)
from alpha import exceptions


class LDAPProvider(JWTProviderMixin):
    """LDAP Identity Provider

    Parameters
    ----------
    connector
        Connector to use for LDAP operations
    search_filter_key, optional
        Key to use for LDAP search filter, by default "uid"
    search_base, optional
        Base DN for LDAP search, by default "cn=users,dc=example,dc=com"
    search_attributes, optional
        Attributes to retrieve during LDAP search, by default
        [ALL_ATTRIBUTES]
    identity_mappings, optional
        Mappings from LDAP attributes to Identity fields, by default
        DEFAULT_LDAP_MAPPINGS
    populate_groups, optional
        Whether to populate groups in the Identity, by default True
    populate_permissions, optional
        Whether to populate permissions in the Identity, by default False
    populate_claims, optional
        Whether to populate claims in the Identity, by default True
    auto_connect, optional
        Whether to automatically connect using the connector, by default
        True
    change_password_supported, optional
        Whether the provider supports changing passwords, by default False
    additional_connector_params, optional
        Additional parameters to pass to the LDAP connection, by default
        {"receive_timeout": 5}
    """

    protocol = "ldap"
    _token_factory: TokenFactory | None = None

    def __init__(
        self,
        connector: LDAPConnector,
        token_factory: TokenFactory | None = None,
        search_filter_key: str = "uid",
        search_base: str = "cn=users,dc=example,dc=com",
        search_attributes: list[str] = [ALL_ATTRIBUTES],
        identity_mappings: dict[str, str] = DEFAULT_LDAP_MAPPINGS,
        populate_groups: bool = True,
        populate_permissions: bool = False,
        populate_claims: bool = True,
        auto_connect: bool = True,
        change_password_supported: bool = False,
        additional_connector_params: dict[str, Any] | None = None,
    ) -> None:
        """Initialize LDAPProvider"""
        self._connector = connector
        self._token_factory = token_factory
        self._search_filter_key = search_filter_key
        self._search_base = search_base
        self._search_attributes = search_attributes
        self._identity_mappings = identity_mappings
        self._populate_groups = populate_groups
        self._populate_permissions = populate_permissions
        self._populate_claims = populate_claims
        self._auto_connect = auto_connect
        self._change_password_supported = change_password_supported
        self._additional_connector_params = additional_connector_params or {
            'receive_timeout': 5
        }
        if self._auto_connect and not self._connector.is_connected():
            self._connector.connect()

    def authenticate(self, credentials: PasswordCredentials) -> Identity:
        """Authenticate a user using LDAP

        Parameters
        ----------
        credentials
            PasswordCredentials object containing username and password

        Returns
        -------
            Identity object

        Raises
        ------
        exceptions.InvalidCredentialsException
            Raised when the provided credentials are invalid
        """
        conn = self._connector.get_connection()

        # Search for user entry
        entry = self._search_user(conn, credentials.username)
        entry_dn = cast(str, entry.entry_dn)  # type: ignore

        # Try to bind with user credentials to verify password
        if not self._verify_password(
            entry_dn=entry_dn, credentials=credentials
        ):
            raise exceptions.InvalidCredentialsException(
                f"Credentials for \'{credentials.username}\' are invalid"
            )

        return self._convert_ldap_entry_to_identity(entry)

    def get_user(self, subject: str) -> Identity:
        """Retrieve a user by the subject

        Parameters
        ----------
        subject
            Subject (username) of the user to retrieve

        Returns
        -------
            Identity object
        """
        conn = self._connector.get_connection()

        # Search for user entry
        entry = self._search_user(conn, subject)

        return self._convert_ldap_entry_to_identity(entry)

    def change_password(
        self, credentials: PasswordCredentials, new_password: str
    ) -> None:
        """Change the password of a user

        Parameters
        ----------
        credentials
            PasswordCredentials object containing username and password
        new_password
            New password to set for the user

        Raises
        ------
        exceptions.NotSupportedException
            Raised when the change password operation is not supported
        exceptions.IdentityError
            Raised when there is an error changing the password
        """
        if not self._change_password_supported:
            raise exceptions.NotSupportedException(
                "Change password operation is not supported by this provider"
            )
        conn = self._connector.get_connection()

        # Search for user entry
        entry = self._search_user(conn, credentials.username)
        entry_dn = cast(str, entry.entry_dn)  # type: ignore

        # Try to bind with user credentials to verify password
        if not self._verify_password(
            entry_dn=entry_dn, credentials=credentials
        ):
            raise exceptions.InvalidCredentialsException(
                f"Credentials for \'{credentials.username}\' are invalid"
            )

        try:
            conn.extend.microsoft.modify_password(  # type: ignore
                entry_dn, new_password
            )
        except LDAPException as e:
            raise exceptions.IdentityError(
                "Failed to change password for user "
                f"\'{credentials.username}\': {str(e)}"
            ) from e

    def _search_user(self, conn: Connection, username: str) -> Entry:
        """Search for a user in LDAP by username

        Parameters
        ----------
        conn
            Connection object to use for LDAP operations
        username
            Username to search for

        Returns
        -------
            Entry object

        Raises
        ------
        exceptions.UserNotFoundException
            Raised when user is not found
        """
        try:
            conn.search(  # type: ignore
                search_base=self._search_base,
                search_filter=f"({self._search_filter_key}={username})",
                attributes=self._search_attributes,
            )
        except LDAPException as e:
            raise exceptions.IdentityError(
                f"Failed to search for user \'{username}\': {str(e)}"
            ) from e

        if not conn.entries:  # type: ignore
            raise exceptions.UserNotFoundException(
                f"User \'{username}\' not found by identity provider"
            )

        return cast(Entry, conn.entries[0])  # type: ignore

    def _verify_password(
        self, entry_dn: str, credentials: PasswordCredentials
    ) -> bool:
        """Verify the password for a given LDAP entry DN

        Parameters
        ----------
        entry_dn
            Distinguished Name of the LDAP entry
        credentials
            PasswordCredentials object containing username and password

        Returns
        -------
        bool
            True if password verification succeeded, False otherwise

        Raises
        ------
        exceptions.InvalidCredentialsException
            Raised when the provided credentials are invalid
        """
        try:
            connection_cls = getattr(
                self._connector, "connection_cls", Connection
            )
            conn = connection_cls(
                self._connector.get_server(),
                user=entry_dn,
                password=credentials.password,
                client_strategy=self._connector._client_strategy,  # type: ignore
                auto_bind=True,
                **self._additional_connector_params,
            )
            try:
                if conn:
                    return True
                return False
            finally:
                conn.unbind()
        except LDAPException as e:
            raise exceptions.InvalidCredentialsException(
                f"Credentials for \'{credentials.username}\' are invalid"
            ) from e

    def _convert_ldap_entry_to_identity(self, entry: Entry) -> Identity:
        """Convert an LDAP entry to an Identity object

        Parameters
        ----------
        entry
            Entry object

        Returns
        -------
            Identity object
        """
        entry_dict = cast(dict[str, Any], entry.entry_attributes_as_dict)  # type: ignore
        identity = Identity.from_ldap_dict(
            entry=entry_dict,
            mappings=self._identity_mappings,
            populate_claims=self._populate_claims,
            populate_groups=self._populate_groups,
            populate_permissions=self._populate_permissions,
        )
        return identity


class ADProvider(LDAPProvider):
    """Active Directory Identity Provider

    Inherits from LDAPProvider with default settings for Active Directory.

    Parameters
    ----------
    connector
        Connector to use for LDAP operations.
    token_factory, optional
        Factory used to create tokens, by default ``None``.
    search_filter_key, optional
        Key to use for Active Directory search filter, by default
        ``"sAMAccountName"``.
    search_base, optional
        Base distinguished name (DN) for Active Directory searches, by default
        ``"CN=users,DC=example,DC=com"``.
    search_attributes, optional
        Attributes to retrieve during Active Directory searches, by default
        ``AD_SEARCH_ATTRIBUTES``.
    identity_mappings, optional
        Mapping of Active Directory attributes to :class:`Identity` fields, by
        default ``DEFAULT_AD_MAPPINGS``.
    populate_groups, optional
        Whether to populate group memberships on the :class:`Identity`, by
        default ``True``.
    populate_permissions, optional
        Whether to populate permissions on the :class:`Identity`, by default
        ``False``.
    populate_claims, optional
        Whether to populate claims on the :class:`Identity`, by default
        ``True``.
    auto_connect, optional
        Whether to automatically open the LDAP connection on first use, by
        default ``True``.
    change_password_supported, optional
        Whether this provider supports changing passwords, by default
        ``False``.
    """

    def __init__(
        self,
        connector: LDAPConnector,
        token_factory: TokenFactory | None = None,
        search_filter_key: str = "sAMAccountName",
        search_base: str = "CN=users,DC=example,DC=com",
        search_attributes: list[str] = AD_SEARCH_ATTRIBUTES,
        identity_mappings: dict[str, str] = DEFAULT_AD_MAPPINGS,
        populate_groups: bool = True,
        populate_permissions: bool = False,
        populate_claims: bool = True,
        auto_connect: bool = True,
        change_password_supported: bool = False,
    ) -> None:
        """Initialize ADProvider"""
        super().__init__(
            connector=connector,
            token_factory=token_factory,
            search_filter_key=search_filter_key,
            search_base=search_base,
            search_attributes=search_attributes,
            identity_mappings=identity_mappings,
            populate_groups=populate_groups,
            populate_permissions=populate_permissions,
            populate_claims=populate_claims,
            auto_connect=auto_connect,
            change_password_supported=change_password_supported,
        )
