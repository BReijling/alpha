from dataclasses import dataclass


@dataclass
class Subparser:
    """An argparse subparser with parameters confirmed to the argparse parser
    parameters and could be extended accordingly.
    """

    name: str
    help: str
