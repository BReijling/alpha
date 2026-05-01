from example.containers.container import Container


def init_container() -> Container:
    container = Container()

    container.config.from_dict(
        {
            "cors": {
                "origins": ["*"],
            }
        }
    )

    container.wire(modules=[__name__])
    return container


def main() -> None:
    print("Hello from example!")
