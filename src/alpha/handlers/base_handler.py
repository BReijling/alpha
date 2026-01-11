from typing import Any


class BaseHandler:
    """Base class for all handlers."""

    def validate_arguments(self, **kwargs: Any) -> None:
        """Validate arguments to handle the command."""
        raise NotImplementedError(
            "validate_arguments method must be implemented by subclasses"
        )

    def set_arguments(self, **kwargs: Any):
        """Set arguments to handle the command."""
        self.validate_arguments(**kwargs)

        for k, v in kwargs.items():
            setattr(self, k, v)
