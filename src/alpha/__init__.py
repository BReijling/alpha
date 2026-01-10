import os

from alpha.containers.container import Container


def init_container() -> Container:
    """Initialize the alpha package container."""
    CONFIG_PATH = os.getenv("CONFIG_PATH", "./config.yaml")

    container = Container()
    container.config.from_yaml(CONFIG_PATH)

    container.wire(modules=[__name__])
    return container
