from typing import Any, Protocol


class Handler(Protocol):
    """Base class or interface for a handler.

    Make sure you implement the __init__ your way, but defining the CLI
    arguments used inside the implemented functions below.
    """

    def handle_command(self) -> None:
        """The function to be implemented to handle the command."""

    def validate_arguments(self, **kwargs: Any) -> None:
        """Function to validate the arguments."""

    def set_arguments(self, **kwargs: Any) -> None:
        """Set arguments to handle the command."""
