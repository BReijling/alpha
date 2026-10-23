from typing import Any, Self


class FromDictMixin:
    """This mixin class provides a method to create an instance of the model
    from a dictionary.
    """

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create an instance of the model from a dictionary.

        Parameters
        ----------
        data
            Dictionary containing model data.

        Returns
        -------
        Self
            A new instance of the model created from the dictionary.
        """
        return cls(**data)
