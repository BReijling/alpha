from dependency_injector import containers, providers

from alpha.factories.jwt_factory import JWTFactory
from alpha.infra.connectors.ldap_connector import LDAPConnector
from alpha.interfaces.token_factory import TokenFactory
from alpha.providers.ldap_provider import LDAPProvider
from alpha.services.authentication_service import AuthenticationService


class Container(containers.DeclarativeContainer):
    """Dependency injection container for the alpha package."""

    config = providers.Configuration()

    # Factories
    token_factory: providers.Factory[TokenFactory] = providers.Factory(
        JWTFactory,
        secret=config.jwt.secret,
        lifetime_hours=config.jwt.lifetime_hours,
        issuer=config.jwt.issuer,
    )

    # Connectors
    ldap_connector: providers.Singleton[LDAPConnector] = providers.Singleton(
        LDAPConnector,
        server_url=config.ldap.server_url,
        server_port=config.ldap.server_port,
        bind_dn=config.ldap.bind_dn,
        bind_password=config.ldap.bind_password,
        use_tls=config.ldap.use_tls,
    )

    # Providers
    ldap_provider: providers.Factory[LDAPProvider] = providers.Factory(
        LDAPProvider,
        connector=ldap_connector,
        token_factory=token_factory,
        search_filter_key=config.ldap.search_filter_key,
        search_base=config.ldap.search_base,
    )

    # Services
    api_service = "mocked_service"
    user_management_service = "mocked_service"
    authentication_service = providers.Factory(
        AuthenticationService,
        identity_provider=ldap_provider,
    )
