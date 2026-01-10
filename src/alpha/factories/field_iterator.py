"""Contains Field & FieldIterator class"""

import dataclasses
import attrs
from pydantic.fields import FieldInfo
from typing import Any

from pydantic_core import MISSING

from alpha.interfaces.attrs_instance import AttrsInstance
from alpha.interfaces.dataclass_instance import DataclassInstance
from alpha.interfaces.pydantic_instance import PydanticInstance
from alpha.utils.is_attrs import is_attrs
from alpha.utils.is_pydantic import is_pydantic


class Field:
    """An object which is used in ModelClassFactory & ClassFactory instances
    to share specific values about class attributes
    """

    def __init__(
        self,
        init: bool,
        name: str,
        type_: Any,
        default: Any,
        default_factory: Any = None,
    ) -> None:
        """Initialize a Field object

        Parameters
        ----------
        init
            init value
        name
            name value
        type_
            type value. Can be an actual type or the string name of the type
            in which case the value will be evaluated to extract the type
        default
            default value
        default_factory, optional
            default value if present, by default None
        """
        self.init = init
        self.name = name
        self.default = default
        self.default_factory = default_factory

        if isinstance(type_, str):
            try:
                self.type = eval(type_)
            except NameError as exc:
                raise NameError(
                    f"Unable to evaluate '{type_}' as a type: {exc}.\n"
                    "A string value is found as type annotation of a class "
                    "attribute. This behavure is probably caused by importing "
                    "__future__.annotations in the module of a data class. "
                    "This behavure is also described in PEP563 "
                    "(https://peps.python.org/pep-0563/). Try not importing "
                    "__future__.annotations."
                )
        else:
            self.type = type_

    def __repr__(self) -> str:
        """Creates a string representation of the object

        Returns
        -------
            string representation of the object
        """
        return (
            "Field("
            f"name={self.name!r},"
            f"type={self.type!r},"
            f"default={self.default!r},"
            f"default_factory={self.default_factory!r},"
            f"init={self.init!r}"
            ")"
        )

    @classmethod
    def from_dataclass(cls, obj: dataclasses.Field[Any]) -> "Field":
        """Create a Field object from a dataclass Field

        Parameters
        ----------
        obj
            dataclass Field

        Returns
        -------
            Field object
        """
        return cls(
            init=obj.init,
            name=obj.name,
            type_=obj.type,
            default=obj.default,
            default_factory=obj.default_factory,
        )

    @classmethod
    def from_attrs(cls, obj: attrs.Attribute) -> "Field":  # type: ignore
        """Create a Field object from a attrs Attribute

        Parameters
        ----------
        obj
            attrs Attribute

        Returns
        -------
            Field object
        """
        return cls(
            init=obj.init,
            name=obj.name,
            type_=obj.type,  # type: ignore
            default=obj.default,  # type: ignore
        )

    @classmethod
    def from_pydantic(cls, key: str, obj: FieldInfo) -> "Field":  # type: ignore
        """Create a Field object from a pydantic Field

        Parameters
        ----------
        obj
            pydantic Field

        Returns
        -------
            Field object
        """
        init = getattr(obj, "init", True)
        type = getattr(obj, "annotation", None)
        default = getattr(obj, "default", MISSING)

        return cls(
            init=init,
            name=key,
            type_=type,
            default=default,
        )


class FieldIterator:
    """A collection of Field objects"""

    def __init__(
        self, obj: DataclassInstance | AttrsInstance | PydanticInstance
    ) -> None:
        """Initialize a FieldIterator by determining the class type of the
        obj argument

        Parameters
        ----------
        obj
            Class of the dataclass or attrs type

        Raises
        ------
        TypeError
            When the obj argument is of an unsupported type
        """
        self._index = 0

        try:
            if dataclasses.is_dataclass(obj):
                self._fields = [
                    Field.from_dataclass(field)
                    for field in dataclasses.fields(obj)
                ]
            elif is_attrs(obj):
                self._fields = [
                    Field.from_attrs(field)  # type: ignore
                    for field in attrs.fields(obj)  # type: ignore
                ]
            elif is_pydantic(obj):
                self._fields = [
                    Field.from_pydantic(key=name, obj=field)  # type: ignore
                    for name, field in obj.model_fields.items()  # type: ignore
                ]
            else:
                raise TypeError(
                    "Incorrect object type. Only a dataclass-, attrs- "
                    "or pydantic class is supported"
                )
        except NameError as exc:
            raise NameError(
                "An error occured while evaluating an attribute of the "
                f"{obj.__name__} class. {exc}"  # type: ignore
            )

    def __iter__(self) -> "FieldIterator":
        """Iter method

        Returns
        -------
            This object
        """
        return self

    def __next__(self) -> Field:
        """Next method

        Returns
        -------
            Next item in the collection

        Raises
        ------
        StopIteration
            Collection out of range
        """
        if self._index < len(self._fields):
            item = self._fields[self._index]
            self._index += 1
            return item
        else:
            raise StopIteration
