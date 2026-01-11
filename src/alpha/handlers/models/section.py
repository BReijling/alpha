from dataclasses import dataclass

from alpha.handlers.models.command import Command
from alpha.handlers.models.subparser import Subparser


@dataclass
class Section(Subparser):
    """A sub argparse parser, used in the first level of a CLI command."""

    description: str
    commands: list[Command]
