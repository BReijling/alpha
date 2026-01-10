"""Contains RequestFactory class"""

import sys
import types
import typing
from enum import Enum
from typing import Any, Callable, get_args, get_origin

from alpha import exceptions
from alpha.factories._type_conversion_matrix import TYPE_CONVERSION_MATRIX
from alpha.factories.model_class_factory import (
    ModelClassFactory,
)
from alpha.factories.type_factories import (
    EnumTypeFactory,
    GenericTypeFactory,
    JsonPatchTypeFactory,
)
from alpha.infra.models.json_patch import JsonPatch
from alpha.interfaces.dataclass_instance import DataclassInstance
from alpha.interfaces.factories import (
    ModelClassFactoryInstance,
    TypeFactory,
)
from alpha.interfaces.openapi_model import OpenAPIModel


class RequestFactory:
    """This class handles API requests"""

    def __init__(
        self,
        func: Callable[[Any], Any],
        cast_args: bool = True,
        use_model_class_factory: bool = True,
        model_class_factory: type[
            ModelClassFactoryInstance
        ] = ModelClassFactory,
        generic_type_factory: type[TypeFactory] = GenericTypeFactory,
        enum_type_factory: type[TypeFactory] = EnumTypeFactory,
        json_patch_type_factory: type[TypeFactory] = JsonPatchTypeFactory,
    ) -> None:
        """Initializing the class with a service function
        The service function will be called when calling
        the cls.__call__ function.

        Parameters
        ----------
        func
            A callable service function
        cast_args, optional
            Make use of the GenericTypeFactory to cast arguments,
            by default True
        use_model_class_factory, optional
            Make use of the ModelClassFactory to map objects to a dataclass,
            by default True
        model_class_factory, optional
            A ModelClassFactory class
            by default ModelClassFactory
        generic_type_factory, optional
            A TypeFactory that can handle generic types
            by default GenericTypeFactory
        enum_type_factory, optional
            A TypeFactory that can handle enum types
            by default EnumTypeFactory
        json_patch_type_factory, optional
            A TypeFactory that can handle a JsonPatch type
            by default JsonPatchTypeFactory
        """
        self.func = func
        self.cast_args = cast_args
        self.use_model_class_factory = use_model_class_factory
        self.model_class_factory = model_class_factory
        self.generic_type_factory = generic_type_factory
        self.enum_type_factory = enum_type_factory
        self.json_patch_type_factory = json_patch_type_factory

    def __call__(self, **kwargs: dict[str, Any]) -> Any:
        """Calling the service function
        Any keyword argument will be parsed by the self._parse_args function
        Each argument will be mapped on the functions parameter type of the
        corresponding keyword.

        The keyword arguments need to match the functions parameters.
        Therefore, *args or **kwargs are not allowed as the functions
        parameters.

        Parameters
        ----------
        kwargs
            Any keyword argument that will be passed to the service function

        Returns
        -------
        Any
            The returned object of the called service function
        """
        annotations = self.func.__annotations__
        params = {
            k: self._parse_args(key=k, value=v, cls=annotations[k])
            for k, v in kwargs.items()
        }

        return self.func(**params)  # type: ignore

    def _parse_args(
        self,
        key: str,
        value: Any,
        cls: Any | list[Any],
    ) -> Any:
        """Parsing each keyword argument

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
        Any
            Mapped objects

        Raises
        ------
        exceptions.ClassMismatchException
            When the source and destination types are not both of an iterable
            type
        """
        union_types = getattr(typing, "_UnionGenericAlias")

        if sys.version_info.minor >= 10:
            union_types = (
                getattr(typing, "_UnionGenericAlias") | types.UnionType
            )

        if isinstance(cls, union_types):
            union_args = get_args(cls)
            if value is None and type(None) in union_args:
                return value
            cls = union_args[0]

        if get_origin(cls) in [list, set, tuple]:
            if type(value) not in [list, set, tuple]:
                raise exceptions.ClassMismatchException(
                    "The targeted object type is an iterable but the source "
                    "object is not"
                )
            arg = get_args(cls)[0]
            return [
                self._parse_args(key=key, value=item, cls=arg)
                for item in value
            ]

        if isinstance(cls, DataclassInstance):
            return self._to_dataclass(value=value, cls=cls)

        if isinstance(cls, type(Enum)):
            return self.enum_type_factory().process(
                key=key, value=value, cls=cls
            )

        if cls == JsonPatch:
            return self.json_patch_type_factory().process(
                key=key, value=value, cls=cls
            )

        if cls in TYPE_CONVERSION_MATRIX.keys() and self.cast_args:
            return self.generic_type_factory().process(
                key=key, value=value, cls=cls
            )

        return value

    def _to_dataclass(
        self, value: OpenAPIModel | Any, cls: DataclassInstance
    ) -> Any:
        """Handling the mapping from an OpenAPI Model instance to a dataclass
        The ModelClassFactory will be used if the cls does not have
        a 'from_dict' method

        Parameters
        ----------
        value
            The argument, which is an OpenAPI Model
        cls
            The class of the corresponding parameter

        Returns
        -------
        dataclass
            Dataclass object

        Raises
        ------
        TypeError
            The value is not an instance of the OpenAPI (Base)Model
        """
        if not isinstance(value, OpenAPIModel):
            raise TypeError(f"Unable to map {type(value)} on dataclass model")

        if hasattr(cls, "from_dict"):
            return getattr(cls, "from_dict")(value.to_dict())

        if self.use_model_class_factory:
            return self.model_class_factory().process(obj=value, cls=cls)
        return value
