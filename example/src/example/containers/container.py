from dependency_injector import containers, providers

from example.services.support import SupportService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    support_service = providers.Factory(SupportService)
