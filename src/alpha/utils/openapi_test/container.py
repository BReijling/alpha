import os

from dependency_injector import containers, providers

from alpha.adapters.sqla_unit_of_work import SqlAlchemyUnitOfWork
from alpha.factories.password_factory import PasswordFactory
from alpha.providers.database_provider import DatabaseProvider
from .models import TestGroup
from .models import TestUser
from .models import TestToken
from alpha.factories.jwt_factory import JWTFactory
from alpha.infra.databases.sql_alchemy import SqlAlchemyDatabase
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.token_factory import TokenFactory
from alpha.repositories.models.repository_model import RepositoryModel
from alpha.repositories.sql_alchemy_repository import SqlAlchemyRepository
from alpha.services.authentication_service import AuthenticationService
from alpha.services.user_lifecycle_management import UserLifecycleManagement
from alpha.utils.openapi_test.orm import TestMapper
from alpha.utils.openapi_test.service import TestService


class Container(containers.DeclarativeContainer):
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
        mapper=TestMapper,
    )

    repositories = providers.List(
        RepositoryModel(
            name="test_users",
            repository=SqlAlchemyRepository[TestUser],
            default_model=TestUser,
            interface=SqlRepository,
        ),
        RepositoryModel(
            name="test_groups",
            repository=SqlAlchemyRepository[TestGroup],
            default_model=TestGroup,
            interface=SqlRepository,
        ),
        RepositoryModel(
            name="test_refresh_tokens",
            repository=SqlAlchemyRepository[TestToken],
            default_model=TestToken,
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
        secret=config.jwt.secret,
        lifetime_hours=config.jwt.lifetime_hours,
    )

    password_factory: providers.Factory[PasswordFactory] = providers.Factory(
        PasswordFactory,
    )
    database_provider: providers.Factory[DatabaseProvider] = providers.Factory(
        DatabaseProvider,
        uow=unit_of_work,
        token_factory=token_factory,
        password_factory=password_factory,
        users_repository_name="test_users",
    )

    authentication_service: providers.Factory[AuthenticationService] = (
        providers.Factory(
            AuthenticationService,
            identity_provider=database_provider,
            use_cookies=config.authentication.use_cookies,
            use_refresh_tokens=config.authentication.use_refresh_tokens,
            cookie_path=config.authentication.cookie_path,
            merge_with_database_users=True,
            merge_with_database_groups=True,
            uow=unit_of_work,
            user_model=TestUser,
            group_model=TestGroup,
            token_model=TestToken,
            users_repository_name="test_users",
            groups_repository_name="test_groups",
            refresh_token_storage="database",
            refresh_token_repository_name="test_refresh_tokens",
            static_user=providers.Factory(
                TestUser,
                id=config.authentication.static_user.username,
                username=config.authentication.static_user.username,
                password=config.authentication.static_user.password,
                role=config.authentication.static_user.role,
                permissions=config.authentication.static_user.permissions,
                admin=config.authentication.static_user.admin,
            ),
        )
    )
    user_management_service: providers.Factory[UserLifecycleManagement] = (
        providers.Factory(
            UserLifecycleManagement,
            uow=unit_of_work,
            users_repository_name="test_users",
            groups_repository_name="test_groups",
            user_model=TestUser,
            group_model=TestGroup,
            password_support=True,
            password_factory=password_factory,
        )
    )

    test_service = providers.Factory(
        TestService,
    )


def init_container():
    container = Container()

    container.config.from_dict(
        {
            "database": {
                "host": os.getenv("TEST_PSQL_HOST", "127.0.0.1"),
                "port": int(os.getenv("TEST_PSQL_PORT", "5432")),
                "username": os.getenv("TEST_PSQL_USERNAME", "postgres"),
                "password": os.getenv("TEST_PSQL_PASSWORD", "postgres"),
                "db_name": os.getenv("TEST_PSQL_DB_NAME", "postgres"),
                "db_type": os.getenv("TEST_PSQL_DB_TYPE", "postgresql"),
            },
            "authentication": {
                "use_cookies": True,
                "use_refresh_tokens": True,
                "cookie_path": "/",
                "static_user": {
                    "username": os.getenv(
                        "TEST_STATIC_USER_USERNAME", "admin"
                    ),
                    "password": os.getenv(
                        "TEST_STATIC_USER_PASSWORD", "admin123"
                    ),
                    "role": os.getenv("TEST_STATIC_USER_ROLE", "ADMIN"),
                    "permissions": [
                        "CREATE",
                        "READ",
                        "UPDATE",
                        "DELETE",
                        "MANAGE_USERS",
                        "MANAGE_SETTINGS",
                        "ALL",
                    ],
                    "admin": True,
                },
            },
            "cors": {
                "origins": ["*"],
            },
            "jwt": {
                "secret": "supersecretkey0123456789",
                "lifetime_hours": 1,
            },
            "logging": {
                "level": "DEBUG",
            },
        }
    )

    return container
