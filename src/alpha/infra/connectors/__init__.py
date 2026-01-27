from alpha.infra.connectors.oidc_connector import (
    OIDCConnector,
    KeyCloakOIDCConnector,
)

# Optional LDAP support - only import if ldap3 is available
try:
    from alpha.infra.connectors.ldap_connector import LDAPConnector  # noqa: F401
    _LDAP_AVAILABLE = True
except ImportError:
    _LDAP_AVAILABLE = False # type: ignore

__all__ = [
    "OIDCConnector",
    "KeyCloakOIDCConnector",
]

# Conditionally add LDAP-related exports if available
if _LDAP_AVAILABLE:
    __all__.extend([
        "LDAPConnector",
    ])
