from dependency_injector import containers, providers

from alpha.adapters.sqla_unit_of_work import SqlAlchemyUnitOfWork
from alpha.domain.models.group import Group
from alpha.domain.models.user import User
from alpha.infra.connectors.ldap_connector import LDAPConnector
from alpha.factories.jwt_factory import JWTFactory
from alpha.infra.databases.sql_alchemy import SqlAlchemyDatabase
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.token_factory import TokenFactory
from alpha.providers.ldap_provider import LDAPProvider
from alpha.repositories.models.repository_model import RepositoryModel
from alpha.repositories.sql_alchemy_repository import SqlAlchemyRepository
from alpha.services.authentication_service import AuthenticationService


class TestContainer(containers.DeclarativeContainer):
    """Dependency injection container for the tests."""

    config = providers.Configuration()

    database = providers.Singleton(
        SqlAlchemyDatabase,
        host=config.database.host,
        port=config.database.port,
        username=config.database.username,
        password=config.database.password,
        db_name=config.database.db_name,
        db_type=config.database.db_type,
        create_schema=False,
        create_tables=True,
    )

    repositories = providers.List(
        RepositoryModel(
            name="users",
            repository=SqlAlchemyRepository[User],
            default_model=User,
            interface=SqlRepository,
        ),
        RepositoryModel(
            name="groups",
            repository=SqlAlchemyRepository[Group],
            default_model=Group,
            interface=SqlRepository,
        ),
    )

    unit_of_work = providers.Factory(
        SqlAlchemyUnitOfWork,
        db=database,
        repos=repositories,
    )

    token_factory: providers.Factory[TokenFactory] = providers.Factory(
        JWTFactory,
        secret_key=config.jwt.secret_key,
        lifetime_hours=config.jwt.lifetime_hours,
    )

    ldap_connector: providers.Factory[LDAPConnector] = providers.Factory(
        LDAPConnector,
        server_url=config.ldap.server_url,
        server_port=config.ldap.server_port,
        use_tls=config.ldap.use_tls,
        bind_dn=config.ldap.bind_dn,
        bind_password=config.ldap.bind_password,
    )
    ldap_provider: providers.Factory[LDAPProvider] = providers.Factory(
        LDAPProvider,
        connector=ldap_connector,
        token_factory=token_factory,
        search_base=config.ldap.search_base,
    )

    authentication_service: providers.Factory[AuthenticationService] = (
        providers.Factory(
            AuthenticationService,
            identity_provider=ldap_provider,
            use_cookies=config.authentication.use_cookies,
            use_refresh_tokens=config.authentication.use_refresh_tokens,
            cookie_path=config.authentication.cookie_path,
            merge_with_database_users=True,
            merge_with_database_groups=True,
            uow=unit_of_work,
        )
    )
