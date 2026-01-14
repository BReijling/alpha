from alpha.adapters.sqla_unit_of_work import SqlAlchemyUnitOfWork
from alpha.factories.jwt_factory import JWTFactory
from alpha.factories.logging_handler_factory import LoggingHandlerFactory
from alpha.factories.model_class_factory import ModelClassFactory
from alpha.domain.models.user import User
from alpha.domain.models.base_model import BaseDomainModel, DomainModel
from alpha.domain.models.life_cycle_base import LifeCycleBase
from alpha.infra.connectors.ldap_connector import LDAPConnector
from alpha.infra.databases.sql_alchemy import SqlAlchemyDatabase
from alpha.infra.models.filter_operators import And, Or, Not
from alpha.infra.models.json_patch import JsonPatch
from alpha.infra.models.order_by import OrderBy, Order
from alpha.infra.models.search_filter import SearchFilter, Operator
from alpha.interfaces.attrs_instance import AttrsInstance
from alpha.interfaces.dataclass_instance import DataclassInstance
from alpha.interfaces.pydantic_instance import PydanticInstance
from alpha.interfaces.openapi_model import OpenAPIModel
from alpha.interfaces.updateable import Updateable
from alpha.interfaces.patchable import Patchable
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
from alpha.providers.ldap_provider import LDAPProvider, ADProvider
from alpha.repositories.models.repository_model import RepositoryModel
from alpha.repositories.sql_alchemy_repository import SqlAlchemyRepository
from alpha.services.authentication_service import AuthenticationService
from alpha.utils.is_attrs import is_attrs
from alpha.utils.is_pydantic import is_pydantic
from alpha.utils.logging_configurator import (
    LoggingConfigurator,
    GunicornLogger,
)
from alpha.utils.logging_level_checker import logging_level_checker
from alpha.utils.response_object import create_response_object
from alpha.utils.verify_identity import verify_identity
from alpha.utils.version_checker import minor_version_gte


from alpha.encoder import JSONEncoder

__all__ = [
    "SqlAlchemyUnitOfWork",
    "JWTFactory",
    "LoggingHandlerFactory",
    "ModelClassFactory",
    "BaseDomainModel",
    "DomainModel",
    "LifeCycleBase",
    "User",
    "LDAPConnector",
    "SqlAlchemyDatabase",
    "And",
    "Or",
    "Not",
    "JsonPatch",
    "OrderBy",
    "Order",
    "SearchFilter",
    "Operator",
    "AttrsInstance",
    "DataclassInstance",
    "PydanticInstance",
    "OpenAPIModel",
    "Updateable",
    "Patchable",
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
    "TokenValidator",
    "TokenFactory",
    "JWTProviderMixin",
    "Identity",
    "DEFAULT_LDAP_MAPPINGS",
    "DEFAULT_AD_MAPPINGS",
    "AD_SEARCH_ATTRIBUTES",
    "PasswordCredentials",
    "Token",
    "LDAPProvider",
    "ADProvider",
    "RepositoryModel",
    "SqlAlchemyRepository",
    "AuthenticationService",
    "is_attrs",
    "is_pydantic",
    "LoggingConfigurator",
    "GunicornLogger",
    "logging_level_checker",
    "create_response_object",
    "verify_identity",
    "minor_version_gte",
    "JSONEncoder",
]
