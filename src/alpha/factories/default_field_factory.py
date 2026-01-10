"""Contains DefaultFieldFactory class"""

from dataclasses import _MISSING_TYPE  # type: ignore
from typing import Any, get_args

from alpha import exceptions
from alpha.factories.field_iterator import Field


class DefaultFieldFactory:
    def process(self, field: Field) -> Any:
        """Processes the default value from the field object of a dataclass
        attribute

        Parameters
        ----------
        field
            field object of a dataclass attribute

        Returns
        -------
            The default value found in the field object

        Raises
        ------
        exceptions.DefaultFactoryException
            - When None is allowed by typing but a default value is missing
            - When a default value is missing and the attribute cannot be empty
            - In case of an unknown error
        """
        if hasattr(field, "default_factory"):
            if callable(field.default_factory):
                return field.default_factory()
        if callable(field.default):
            return field.default()
        if not isinstance(field.default, _MISSING_TYPE):
            return field.default
        if type(None) in get_args(field.type):
            raise exceptions.DefaultFactoryException(
                f'None is allowed by typing for the "{field.name}" '
                "attribute, but a default value is missing"
            )
        if isinstance(field.default, _MISSING_TYPE):  # type: ignore
            raise exceptions.DefaultFactoryException(
                f'The source object has no "{field.name}" attribute and no '
                "default value is set"
            )
        raise exceptions.DefaultFactoryException(
            "Unknown default_factory exception"
        )
