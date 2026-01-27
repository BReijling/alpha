from alpha.infra.databases.sql_alchemy import SqlAlchemyDatabase
from alpha.infra.models.filter_operators import And, Or
from alpha.infra.models.json_patch import JsonPatch
from alpha.infra.models.order_by import OrderBy, Order
from alpha.infra.models.search_filter import SearchFilter, Operator

# Optional LDAP support - only import if ldap3 is available
try:
    from alpha.infra.connectors.ldap_connector import LDAPConnector  # noqa: F401
    _LDAP_AVAILABLE = True
except ImportError:
    _LDAP_AVAILABLE = False # type: ignore

__all__ = [
    "SqlAlchemyDatabase",
    "And",
    "Or",
    "JsonPatch",
    "OrderBy",
    "Order",
    "SearchFilter",
    "Operator",
]

# Conditionally add LDAP-related exports if available
if _LDAP_AVAILABLE:
    __all__.extend([
        "LDAPConnector",
    ])
