"""Contains these TypeFactory classes:
- GenericTypeFactory
- DatetimeTypeFactory
- EnumTypeFactory
- JsonPatchTypeFactory
"""

import datetime
from typing import Any, Iterable

import pandas as pd

from alpha import exceptions
from alpha.factories._type_conversion_matrix import TYPE_CONVERSION_MATRIX
from alpha.interfaces.openapi_model import OpenAPIModel


class GenericTypeFactory:
    """An implementation of TypeFactory which is able if process objects of
    type 'type'
    """

    def process(
        self, key: str, value: Any, cls: type, **kwargs: dict[str, Any]
    ) -> Any:
        """Processing generic object types

        Parameters
        ----------
        key
            Keyword of the argument. Used for logging purposes
        value
            The value object
        cls
            The targeted class

        Returns
        -------
            An instance of the targeted class

        Raises
        ------
        exceptions.ObjectConversionNotSupported
            When conversion of the value is not supported
        exceptions.ObjectConversionError
            When an error occured when trying to convert the value to a cls
            instance
        exceptions.ObjectConversionNotAllowed
            When conversion of the value is not allowed
        """
        from_type: Any = type(value)

        try:
            allowed: bool = TYPE_CONVERSION_MATRIX[from_type][cls]
        except KeyError as exc:
            raise exceptions.ObjectConversionNotSupported(
                "Unable to convert an object, because the source "
                f" ({from_type.__name__}) or target ({cls.__name__}) type "
                "is not supported"
            ) from exc

        if allowed:
            try:
                return cls(value)
            except ValueError as exc:
                raise exceptions.ObjectConversionError(
                    f"Unable to convert a(n) {from_type.__name__} "
                    f"to a(n) {cls.__name__}"  # type: ignore
                ) from exc
        raise exceptions.ObjectConversionNotAllowed(
            f"Converting '{key}' which is a(n) {from_type.__name__} class"
            f"to a(n) {str(cls.__name__)} is not allowed"  # type: ignore
        )


class DatetimeTypeFactory:
    """An implementation of TypeFactory which is able if process objects of
    type 'datetime'
    """

    def process(
        self,
        key: str,
        value: datetime.datetime | datetime.date | str,
        cls: type,
        **kwargs: dict[str, Any],
    ) -> datetime.datetime | datetime.date:
        """Processing datetime object types

        Parameters
        ----------
        key
            Keyword of the argument. Not used in this class
        value
            A datetime instance or datetime formatted string
        cls
            A datetime class

        Returns
        -------
            A datetime instance
        """
        if isinstance(value, cls):
            return value  # type: ignore

        day_first = True if kwargs.get("day_first", False) else False

        date_time = pd.to_datetime(  # type: ignore
            value, dayfirst=day_first
        ).to_pydatetime()
        if cls == datetime.date:
            return date_time.date()
        return date_time


class EnumTypeFactory:
    """An implementation of TypeFactory which is able if process objects of
    type 'Enum'
    """

    def process(
        self, key: str, value: Any, cls: Any, **kwargs: dict[str, Any]
    ) -> Any:
        """Creates Enum objects from either a Enum name or value

        Parameters
        ----------
        key
            Keyword of the argument
        value
            The argument
        cls
            The class of the corresponding parameter

        Returns
        -------
        Enum
            An Enum object

        Raises
        ------
        AttributeError
            Not a valid Enum name or value
        """
        try:
            if not value:
                try:
                    return getattr(cls, "NONE")
                except AttributeError:
                    return None
            if isinstance(value, str):
                return getattr(cls, str(value).upper())
            return cls(value)  # type: ignore
        except AttributeError as exc:
            raise AttributeError(
                f"{value} is not a valid Enum name for the {key} attribute"
            ) from exc


class JsonPatchTypeFactory:
    """An implementation of TypeFactory which is able if process objects of
    type 'JsonPatch'
    """

    def process(
        self, key: str, value: Any, cls: Any, **kwargs: dict[str, Any]
    ) -> Any:
        """Processing JsonPatch object types

        Parameters
        ----------
        key
            Keyword of the argument. Used for logging purposes
        value
            An iterable containing OpenAPIModel with 'op', 'path' and 'value'
            attributes
        cls
            The targeted class, which should always be JsonPatch

        Returns
        -------
            An instance of the targeted class

        Raises
        ------
        AttributeError
            - When value is not an iterable
            - When value is an empty iterable
            - When value does not contain OpenAPIModel instances
        """
        if not isinstance(value, Iterable):
            raise AttributeError(f"The {key} attribute has to be an iterable")
        if len(value) == 0:  # type: ignore
            raise AttributeError(
                f"The {key} attribute cannot be an empty iterable"
            )
        if isinstance(value[0], OpenAPIModel):  # type: ignore
            patches: list[OpenAPIModel] = value  # type: ignore
            return cls([patch.to_dict() for patch in patches])  # type: ignore
        else:
            raise AttributeError(
                f"The {key} attribute has to be an iterable containing "
                "OpenAPIModel objects of a JsonPatch type"
            )
