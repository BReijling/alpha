import argparse
import os
import sys
import tomllib
from dependency_injector.wiring import Provide, inject

from alpha.containers.container import Container
from alpha.handlers.models.section import Section


@inject
def main(sections: list[Section] = Provide[Container.sections]) -> None:
    """Entry point for the alpha cli.

    Parameters
    ----------
    sections: List[Section]
        List of sections to include in the cli.
    """

    # Create the main parser
    parser = argparse.ArgumentParser(
        description='Alpha command line interface.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        title='Use one of the sub categories to run commands on',
        dest='section',
    )

    # Parser dict to store in all parsers to match later on when finding a
    # handler.
    section_parsers = {}
    command_parsers = {}

    # Create all sections
    for section in sections:
        command_parsers[section.name] = {}
        section_parsers[section.name] = subparsers.add_parser(
            section.name,
            description=section.description,
            help=section.help,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        section_subparser = section_parsers[section.name].add_subparsers(
            dest='command'
        )

        # Create all commands per section
        for command in section.commands:
            command_parsers[section.name][command.name] = (
                section_subparser.add_parser(
                    command.name,
                    help=command.help,
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                )
            )

            # Add all arguments for a command
            for argument in command.arguments:
                command_parsers[section.name][command.name].add_argument(
                    argument.name,
                    help=argument.help,
                    default=argument.default,
                    **argument.args,
                )

    # Do the handling for the given section and command in the CLI
    section_argument = None
    command_argument = None
    args = parser.parse_args()

    try:
        section_argument = args.section
        command_argument = args.command
    except AttributeError:
        parser.print_help()
        return

    if not section_argument:
        # Can not occur, but just in case. Should be handled above
        return

    if not command_argument:
        section_parsers[section_argument].print_help()
        return

    # Get all arguments and remove the section and command so they can be
    # 'kwarged' into the Handler set_arguments function.
    handler_args = vars(args)
    del handler_args['section']
    del handler_args['command']

    # Find the right handler
    for section in sections:
        for command in section.commands:
            if (
                section.name == section_argument
                and command.name == command_argument
            ):
                command.handler.set_arguments(**handler_args)
                command.handler.handle_command()
                return

    print('No handler found, you should never read this')
    return


def _guess_current_package_name() -> str:
    """Guess the name of the python package where you are generating the API
    for. If a pyproject.toml file can be found the name is read from there. If
    not, it looks for a subfolder which contains a python package.

    Returns
    -------
    str
        The guessed package name.
    """

    cwd = os.getcwd()
    pyproject_path = os.path.join(cwd, 'pyproject.toml')

    # look for pyproject.toml file in subfolders
    if not os.path.isfile(pyproject_path):
        for entry in os.scandir(cwd):
            if not entry.is_dir():
                continue
            possible_path = os.path.join(entry.path, 'pyproject.toml')
            if os.path.isfile(possible_path):
                pyproject_path = possible_path
                break

    if os.path.isfile(pyproject_path):
        try:
            with open(pyproject_path, 'rb') as f:
                pyproject_data = tomllib.load(f)
                return pyproject_data['project']['name'].replace('-', '_')
        except Exception:
            pass

    # Fallback to use the current folder name
    print('Could not find pyproject.toml, guessing package name from folder')
    return os.path.basename(cwd)


def init() -> None:
    """Init the container and wire it to the main function."""
    container = Container()
    guessed_name = _guess_current_package_name()
    if guessed_name:
        container.config.api_package_name.from_value(f'{guessed_name}_api')
        container.config.service_package_name.from_value(guessed_name)
        container.config.container_import.from_value(
            f'from {guessed_name}.containers.container import Container'
        )
        container.config.init_container_from.from_value(guessed_name)
        container.config.init_container_function.from_value('init_container')
    container.wire(modules=[sys.modules[__name__]])

    main()
