from dependency_injector import containers, providers

from alpha.handlers.api_generate_handler import ApiGenerateHandler
from alpha.handlers.api_run_handler import ApiRunHandler
from alpha.handlers.models.command import Command
from alpha.handlers.models.section import Section
from alpha.handlers.models.argument import Argument


class Container(containers.DeclarativeContainer):
    """Dependency injection container for the alpha package."""

    config = providers.Configuration()

    api_gen_command = providers.Factory(
        Command,
        name='gen',
        help=(
            "Generate the API code and watch OpenAPI spec file. The API code "
            "will be generated into the ./api folder."
        ),
        handler=providers.Factory(ApiGenerateHandler),
        arguments=providers.List(
            providers.Factory(
                Argument,
                default='specification/openapi.yaml',
                name='--spec-file',
                help='Path to the specification file',
                args={
                    'type': str,
                    'nargs': '?',
                },
            ),
            providers.Factory(
                Argument,
                default=config.api_package_name,
                name='--api-package',
                help=(
                    "Name of the API package to generate. Automatically "
                    "determined or guessed. If incorrect, "
                    "just use this argument."
                ),
                args={
                    'type': str,
                    'nargs': '?',
                },
            ),
            providers.Factory(
                Argument,
                default=config.service_package_name,
                name='--service-package',
                help=(
                    "Name of the service package to use. Automatically "
                    "determined or guessed. If incorrect, "
                    "just use this argument."
                ),
                args={
                    'type': str,
                    'nargs': '?',
                },
            ),
            providers.Factory(
                Argument,
                default=config.container_import,
                name='--container-import',
                help=(
                    "Name of the container to use. Automatically "
                    "determined or guessed. If incorrect, "
                    "just use this argument. When no container is used, "
                    "use empty string for this variable"
                ),
                args={
                    'type': str,
                    'nargs': '?',
                },
            ),
            providers.Factory(
                Argument,
                default=config.init_container_from,
                name='--init-container-from',
                help=(
                    "Location of where the container initialize function "
                    "should be imported from."
                ),
                args={
                    'type': str,
                    'nargs': '?',
                },
            ),
            providers.Factory(
                Argument,
                default=config.init_container_function,
                name='--init-container-function',
                help="Name of the container initialize function.",
                args={
                    'type': str,
                    'nargs': '?',
                },
            ),
            providers.Factory(
                Argument,
                default='post_process.py',
                name='--post-process-file',
                help="Path to the post process file to use after generation",
                args={
                    'type': str,
                    'nargs': '?',
                },
            ),
            providers.Factory(
                Argument,
                default='python-flask',
                name='--generator-name',
                help="Name of the openapi generator to use",
                args={
                    'type': str,
                    'nargs': '?',
                },
            ),
            providers.Factory(
                Argument,
                default=False,
                name='--no-watch',
                help=(
                    "To prevent watching the spec file for changes and only "
                    "run the generation once."
                ),
                args={
                    'action': 'store_true',
                },
            ),
            providers.Factory(
                Argument,
                default=False,
                name='--templates-only',
                help=(
                    "Only create a templates folder containing openapi "
                    "mustache templates in the current working directory. "
                    "Skip generation of API code."
                ),
                args={
                    'action': 'store_true',
                },
            ),
        ),
    )

    api_run_command = providers.Factory(
        Command,
        name='run',
        help='Run API in development mode',
        handler=providers.Factory(ApiRunHandler),
        arguments=providers.List(
            providers.Factory(
                Argument,
                default=config.api_package_name,
                name='--api-package',
                help='Name of the API package to generate',
                args={
                    'type': str,
                    'nargs': '?',
                },
            ),
            providers.Factory(
                Argument,
                default='8080',
                name='--port',
                help='Port to run server on',
                args={
                    'type': str,
                    'nargs': '?',
                },
            ),
        ),
    )

    api_section = providers.Factory(
        Section,
        name='api',
        description='OpenAPI development commands.',
        help=(
            "All commands for generating and developing an API using the "
            "OpenAPI standards"
        ),
        commands=providers.List(api_gen_command, api_run_command),
    )

    sections = providers.List(
        api_section,
    )
