from alpha.adapters.rest_api_unit_of_work import RestApiUnitOfWork
from alpha.adapters.sqla_unit_of_work import SqlAlchemyUnitOfWork
from alpha.factories.jwt_factory import JWTFactory
from alpha.factories.logging_handler_factory import LoggingHandlerFactory
from alpha.factories.model_class_factory import ModelClassFactory
from alpha.domain.models.user import User
from alpha.domain.models.group import Group
from alpha.domain.models.role import Role
from alpha.domain.models.base_model import (
    BaseDomainModel,
    DomainModel,
    DomainModelCovariant,
    DomainModelContravariant,
)
from alpha.domain.models.life_cycle_base import LifeCycleBase
from alpha.infra.connectors.oidc_connector import (
    OIDCConnector,
    KeyCloakOIDCConnector,
)
from alpha.infra.connectors.sql_alchemy import SqlAlchemyDatabase
from alpha.infra.models.filter_operators import And, Or
from alpha.infra.models.json_patch import JsonPatch
from alpha.infra.models.order_by import OrderBy, Order
from alpha.infra.models.search_filter import SearchFilter, Operator
from alpha.interfaces.attrs_instance import AttrsInstance
from alpha.interfaces.dataclass_instance import DataclassInstance
from alpha.interfaces.pydantic_instance import PydanticInstance
from alpha.interfaces.openapi_model import OpenAPIModel
from alpha.interfaces.updatable import Updatable
from alpha.interfaces.patchable import Patchable
from alpha.interfaces.api_repository import ApiRepository
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.sql_mapper import SqlMapper
from alpha.interfaces.sql_database import SqlDatabase
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.interfaces.providers import (
    IdentityProvider,
    PasswordAuthenticator,
    UserDirectory,
    PasswordChanger,
    TokenIssuer,
    TokenValidator,
)
from alpha.interfaces.token_factory import TokenFactory
from alpha.mixins.jwt_provider import JWTProviderMixin
from alpha.providers.models.identity import (
    Identity,
    DEFAULT_LDAP_MAPPINGS,
    DEFAULT_AD_MAPPINGS,
    AD_SEARCH_ATTRIBUTES,
)
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.token import Token
from alpha.providers.oidc_provider import OIDCProvider, KeyCloakProvider
from alpha.repositories.models.repository_model import RepositoryModel
from alpha.repositories.rest_api_repository import RestApiRepository
from alpha.repositories.sql_alchemy_repository import SqlAlchemyRepository
from alpha.services.authentication_service import AuthenticationService
from alpha.services.user_lifecycle_management import UserLifecycleManagement
from alpha.utils.is_attrs import is_attrs
from alpha.utils.is_pydantic import is_pydantic
from alpha.utils.logging_configurator import (
    LoggingConfigurator,
    GunicornLogger,
)
from alpha.utils.logging_level_checker import logging_level_checker
from alpha.utils.request_headers import Headers
from alpha.utils.response_object import create_response_object
from alpha.utils.verify_identity import verify_identity
from alpha.utils.version_checker import minor_version_gte
from alpha.encoder import JSONEncoder

# Optional LDAP support - only import if ldap3 is available
try:
    from alpha.infra.connectors.ldap_connector import (
        LDAPConnector,  # noqa: F401
    )
    from alpha.providers.ldap_provider import (
        LDAPProvider,  # noqa: F401
        ADProvider,  # noqa: F401
    )

    _LDAP_AVAILABLE = True
except ImportError:
    _LDAP_AVAILABLE = False  # type: ignore

__all__ = [
    "RestApiUnitOfWork",
    "SqlAlchemyUnitOfWork",
    "JWTFactory",
    "LoggingHandlerFactory",
    "ModelClassFactory",
    "BaseDomainModel",
    "DomainModel",
    "DomainModelCovariant",
    "DomainModelContravariant",
    "LifeCycleBase",
    "User",
    "Group",
    "Role",
    "OIDCConnector",
    "KeyCloakOIDCConnector",
    "SqlAlchemyDatabase",
    "And",
    "Or",
    "JsonPatch",
    "OrderBy",
    "Order",
    "SearchFilter",
    "Operator",
    "AttrsInstance",
    "DataclassInstance",
    "PydanticInstance",
    "OpenAPIModel",
    "Updatable",
    "Patchable",
    "ApiRepository",
    "SqlRepository",
    "SqlMapper",
    "SqlDatabase",
    "UnitOfWork",
    "IdentityProvider",
    "PasswordAuthenticator",
    "TokenValidator",
    "UserDirectory",
    "PasswordChanger",
    "TokenIssuer",
    "TokenFactory",
    "JWTProviderMixin",
    "Identity",
    "DEFAULT_LDAP_MAPPINGS",
    "DEFAULT_AD_MAPPINGS",
    "AD_SEARCH_ATTRIBUTES",
    "PasswordCredentials",
    "Token",
    "OIDCProvider",
    "KeyCloakProvider",
    "RepositoryModel",
    "RestApiRepository",
    "SqlAlchemyRepository",
    "AuthenticationService",
    "UserLifecycleManagement",
    "is_attrs",
    "is_pydantic",
    "LoggingConfigurator",
    "GunicornLogger",
    "logging_level_checker",
    "Headers",
    "create_response_object",
    "verify_identity",
    "minor_version_gte",
    "JSONEncoder",
]


# Conditionally add LDAP-related exports if available
if _LDAP_AVAILABLE:
    __all__.extend(
        [
            "LDAPConnector",
            "LDAPProvider",
            "ADProvider",
        ]
    )


def _ensure_ast_str_compat() -> None:
    """Provide ast.Str compatibility for Python 3.14+.

    Older Werkzeug versions (used by Flask 1.x) still instantiate ast.Str.
    Python 3.14 removed that alias, so we recreate it with ast.Constant.
    """
    if hasattr(ast, "Str"):
        return

    class _StrCompat(ast.Constant):
        def __new__(cls, s: str = "", **kwargs):  # noqa: N804
            return ast.Constant(value=s, **kwargs)

    setattr(ast, "Str", _StrCompat)


try:
    import ast

    _ensure_ast_str_compat()
except ImportError:
    pass
