from dataclasses import dataclass

from alpha.handlers.models.argument import Argument
from alpha.handlers.models.subparser import Subparser
from alpha.interfaces.handler import Handler


@dataclass
class Command(Subparser):
    """A sub argparse parser, used in the second level of a
    CLI command.
    """

    handler: Handler
    arguments: list[Argument]
