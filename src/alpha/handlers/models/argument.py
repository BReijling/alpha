from dataclasses import dataclass
from typing import Any


@dataclass
class Argument:
    """An argument which will be assigned to an argparse argument and could be
    extended accordingly.
    """

    name: str
    help: str
    args: dict[str, Any]
    default: str | None = None
