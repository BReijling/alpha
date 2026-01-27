# Models
from alpha.providers.models.identity import (
    Identity,
    DEFAULT_LDAP_MAPPINGS,
    DEFAULT_AD_MAPPINGS,
    AD_SEARCH_ATTRIBUTES,
)
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.token import Token

# Providers
from alpha.providers.oidc_provider import OIDCProvider, KeyCloakProvider

# Optional LDAP support - only import if ldap3 is available
try:
    from alpha.providers.ldap_provider import LDAPProvider, ADProvider  # noqa: F401
    _LDAP_AVAILABLE = True
except ImportError:
    _LDAP_AVAILABLE = False # type: ignore

__all__ = [
    "Identity",
    "DEFAULT_LDAP_MAPPINGS",
    "DEFAULT_AD_MAPPINGS",
    "AD_SEARCH_ATTRIBUTES",
    "PasswordCredentials",
    "Token",
    "OIDCProvider",
    "KeyCloakProvider",
]

# Conditionally add LDAP-related exports if available
if _LDAP_AVAILABLE:
    __all__.extend([
        "LDAPProvider",
        "ADProvider",
    ])
