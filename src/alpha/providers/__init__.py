# Models
from typing import Any

from alpha.providers.models.identity import (
    Identity,
    DEFAULT_LDAP_MAPPINGS,
    DEFAULT_AD_MAPPINGS,
    AD_SEARCH_ATTRIBUTES,
)
from alpha.providers.models.credentials import (
    PasswordCredentials,
    PasswordCredentialsUpdate,
)
from alpha.providers.models.token import Token

# Providers


# Optional LDAP support - only import if ldap3 is available
try:
    from alpha.providers.ldap_provider import LDAPProvider, ADProvider  # noqa: F401

    _LDAP_AVAILABLE = True
except ImportError:
    _LDAP_AVAILABLE = False  # type: ignore

__all__ = [
    "Identity",
    "DEFAULT_LDAP_MAPPINGS",
    "DEFAULT_AD_MAPPINGS",
    "AD_SEARCH_ATTRIBUTES",
    "PasswordCredentials",
    "PasswordCredentialsUpdate",
    "Token",
    # "OIDCProvider",
    # "KeyCloakProvider",
]

# Conditionally add LDAP-related exports if available
if _LDAP_AVAILABLE:
    __all__.extend(
        [
            "LDAPProvider",
            "ADProvider",
        ]
    )


def __getattr__(name: str) -> Any:
    if name in {"OIDCProvider", "KeyCloakProvider"}:
        from alpha.providers.oidc_provider import (
            OIDCProvider,
            KeyCloakProvider,
        )

        imported_classes: dict[str, Any] = {
            "OIDCProvider": OIDCProvider,
            "KeyCloakProvider": KeyCloakProvider,
        }

        __all__.extend(list(imported_classes.keys()))

        return imported_classes[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
