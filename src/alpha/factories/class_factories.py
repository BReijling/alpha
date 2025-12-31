"""Contains these ClassFactory classes:
- IterableClassFactory
- DictClassFactory
- DataclassClassFactory
- GenericAliasClassFactory
- UnionClassFactory
- NativeClassFactory
- EnumClassFactory
- AnyClassFactory
"""

import enum
import sys
import types
import typing
from dataclasses import is_dataclass
from typing import Any, Iterable, Optional, Union, get_args, get_origin

from alpha import exceptions
from alpha.factories._type_mapping import TYPES
from alpha.factories.field_iterator import Field
from alpha.infra.models.json_patch import JsonPatch
from alpha.interfaces.factories import (
    FactoryClassesInstance,
)
from alpha.interfaces.openapi_model import OpenAPIModel
from alpha.utils.is_attrs import is_attrs


class IterableClassFactory:
    def process(
        self,
        obj: OpenAPIModel,
        field: Field,
        factory_classes: FactoryClassesInstance,
    ) -> Any:
        """Processing iterable classes. Mapping the items of the corresponding
        OpenAPIModel instance attribute and return them in an iterable of the
        field.type

        Parameters
        ----------
        obj
            OpenAPIModel instance
        field
            Field object of dataclass attribute
        factory_classes
            FactoryClasses instance which acts as a toolbox of Factory classes

        Returns
        -------
            The new iterable object

        Raises
        ------
        exceptions.TypingFactoryException
            Unable to convert an iterable to a certain iterable type
        """
        field_type_origin = get_origin(field.type)
        field_args = get_args(field.type)

        values: Union[Iterable[Any], Any, None] = getattr(
            obj, field.name, None
        )

        if not isinstance(values, Iterable):
            values = [values]

        cls = field_args[0]

        if is_dataclass(cls) or is_attrs(cls):
            if factory_classes.model_class_factory is None:
                raise ValueError(
                    "ModelClassFactory instance is not present in "
                    "FactoryClasses instance"
                )
            collection = [
                factory_classes.model_class_factory.process(obj=obj, cls=cls)
                for obj in values
            ]
        else:
            if not getattr(obj, field.name, None):
                return factory_classes.default_factory.process(field=field)

            if isinstance(cls, type(enum.Enum)):
                type_factory = factory_classes.type_factories["enum"]
            else:
                try:
                    type_factory = TYPES[cls]()
                except KeyError as exc:
                    raise exceptions.ClassFactoryException(
                        "The class of this object type is not supported. "
                        f"{field.type=}; "
                        f"{field_type_origin=}; "
                        f"{field.type.__class__=}; "
                    ) from exc

            collection = [
                type_factory.process(
                    key=field.name,
                    value=val,
                    cls=cls,
                )
                for val in values
            ]

        try:
            if field_type_origin:
                result = field_type_origin(collection)
                return result
        except ValueError as exc:
            raise exceptions.TypingFactoryException(
                "Unable to convert a collection of "
                f"{type(collection[0])} "
                f"instances to a {field_type_origin}: {exc}"
            ) from exc


class DictClassFactory:
    def process(
        self,
        obj: OpenAPIModel,
        field: Field,
        factory_classes: FactoryClassesInstance,
    ) -> Any:
        """Processing dictionary classes. Considering multiple options to get a
        dictionary from an object.

        Parameters
        ----------
        obj
            OpenAPIModel instance
        field
            Field object of dataclass attribute
        factory_classes
            Unused for this implementation of the ClassFactory interface

        Returns
        -------
            Dictionary object

        Raises
        ------
        exceptions.ObjectConversionError
            Unable to return a dictionary
        """
        value: Union[dict[str, Any], Any] = getattr(obj, field.name, None)

        if isinstance(value, dict):
            return value
        if hasattr(value, "to_dict"):
            return getattr(value, "to_dict")()
        if hasattr(value, "_asdict"):
            return getattr(value, "_asdict")()
        if hasattr(value, "__dict__"):
            return value.__dict__
        try:
            return dict(value)
        except (TypeError, ValueError) as exc:
            raise exceptions.ObjectConversionError(
                f'Unable to convert a(n) "{type(value)}" object to a dict'
            ) from exc


class DataclassClassFactory:
    def process(
        self,
        obj: OpenAPIModel,
        field: Field,
        factory_classes: FactoryClassesInstance,
    ) -> Any:
        """Processing dataclass classes by using the model_class_factory from
        the factory_class instance

        Parameters
        ----------
        obj
            OpenAPIModel instance
        field
            Field object of dataclass attribute
        factory_classes
            FactoryClasses instance which acts as a toolbox of Factory classes

        Returns
        -------
            DataclassInterface object

        Raises
        ------
        ValueError
            factory_classes.model_class_factory is None
        """
        if hasattr(obj, field.name):
            obj = getattr(obj, field.name)
        type_ = field.type
        if factory_classes.model_class_factory is None:
            raise ValueError(
                "ModelClassFactory instance is not present in FactoryClasses "
                "instance"
            )
        return factory_classes.model_class_factory.process(obj=obj, cls=type_)


class GenericAliasClassFactory:
    def process(
        self,
        obj: OpenAPIModel,
        field: Field,
        factory_classes: FactoryClassesInstance,
    ) -> Any:
        """Processing generic alias types. Built-in type subclasses from both
        typing._GenericAlias and types.GenericAlias are supported. It uses the
        ClassFactory for iterables and dictionaries, from the class_factories
        attribute of the FactoryClassesInstance, to process each type.

        These examples are all supported:
            - dict[str, Any]
            - typing.Tuple[int]
            - set[float]
            - list[Object]

        An exception will be raised when a union argument is used because only
        one argument (two in case of a dict) is supported.

        Parameters
        ----------
        obj
            OpenAPIModel instance
        field
            Field object of dataclass attribute
        factory_classes
            FactoryClasses instance which acts as a toolbox of Factory classes

        Returns
        -------
            An iterable or a dictionary

        Raises
        ------
        exceptions.MixedArgumentTypesError
            Unable to process a union argument type. eg: list[int | float]
        exceptions.TypingFactoryException
            Catching any future generic alias type
        """
        field_type = get_origin(field.type)
        field_args = get_args(field.type)

        arg_classes = [
            getattr(typing, "_UnionGenericAlias"),
        ]
        if sys.version_info.minor >= 10:  # Backwards compatible with <3.10
            arg_classes.append(getattr(types, "UnionType"))

        for arg in field_args:
            if arg.__class__ in arg_classes:
                raise exceptions.MixedArgumentTypesError(
                    f"Mixed object types in a '{field_type}' are not allowed"
                )

        if field_type in (list, tuple, set, frozenset):
            return factory_classes.class_factories["iterable"].process(
                obj=obj,
                field=field,
                factory_classes=factory_classes,
            )
        if field_type is dict:
            return factory_classes.class_factories["dict"].process(
                obj=obj,
                field=field,
                factory_classes=factory_classes,
            )
        raise exceptions.TypingFactoryException(
            f"Mapping a '{field_type}' type is not supported"
        )


class UnionClassFactory:
    def process(
        self,
        obj: OpenAPIModel,
        field: Field,
        factory_classes: FactoryClassesInstance,
    ) -> Any:
        """Processing union types. Both typing._UnionGenericAlias and
        types.UnionType are supported, eg. `typing.Union[int, float]` or
        `int | float`.

        These rules are being applied:
            - If the first argument is a dataclass or attrs class all other
            arguments will be ignored
            - If the value is of one of the types in the union arguments the
            value will be returned untouched
            - If the value type is not in the union arguments, the value will
            be processed by the GenericTypeClass, to try to map the
            value to match the type of the first union argument

        Parameters
        ----------
        obj
            OpenAPIModel instance
        field
            Field object of dataclass attribute
        factory_classes
            FactoryClasses instance which acts as a toolbox of Factory classes

        Returns
        -------
            Any value with a type of one of the union arguments

        Raises
        ------
        ValueError
            factory_classes.model_class_factory is None
        exceptions.UnionArgumentError
            The attributes value of the OpenAPIModel instance is not compatible
            with one of the types in the union type arguments
        """
        value = getattr(obj, field.name, None)
        if not value:
            return factory_classes.default_factory.process(field=field)

        args = get_args(field.type)
        cls = args[0]

        if is_dataclass(cls) or is_attrs(cls):
            if factory_classes.model_class_factory is None:
                raise ValueError(
                    "ModelClassFactory instance is not present in "
                    "FactoryClasses instance"
                )
            return factory_classes.model_class_factory.process(
                obj=obj, cls=cls
            )
        if type(value) in args:
            return value
        try:
            return factory_classes.type_factories["generic"].process(
                key=field.name, value=value, cls=cls
            )
        except Exception as exc:
            raise exceptions.UnionArgumentError(
                f"{cls} is of a type that is not compatible with the type "
                + "arguments in the union. Casting the value is not possible"
            ) from exc


class NativeClassFactory:
    def process(
        self,
        obj: OpenAPIModel,
        field: Field,
        factory_classes: FactoryClassesInstance,
    ) -> Optional[Any]:
        """Processing native types. Native types are all types that have a
        `type` value for the `__class__` attribute.

        The supported types are present in the keys of the TYPES constant and
        are processed by their corresponding type factories. A dataclass or
        attrs type class will be processed by the DataclassClassFactory.

        Parameters
        ----------
        obj
            OpenAPIModel instance
        field
            Field object of dataclass attribute
        factory_classes
            FactoryClasses instance which acts as a toolbox of Factory classes

        Returns
        -------
            Any value which is returned by another Factory

        Raises
        ------
        KeyError
            In case the type is not present in TYPES
        """
        # Backwards compatibility for python 3.9/10
        if get_args(field.type):
            return factory_classes.class_factories["generic_alias"].process(
                obj=obj, field=field, factory_classes=factory_classes
            )

        value = getattr(obj, field.name, None)
        cls: type = field.type  # type: ignore

        # return the value untouched if it is an instance of cls
        if isinstance(value, cls):
            return value

        if is_dataclass(cls) or is_attrs(cls):
            return factory_classes.class_factories["dataclass"].process(
                obj=obj, field=field, factory_classes=factory_classes
            )
        if cls == JsonPatch:
            return factory_classes.class_factories["json_patch"].process(
                obj=obj, field=field, factory_classes=factory_classes
            )
        try:
            if value:
                type_factory = TYPES[cls]
                return type_factory().process(
                    key=field.name,
                    value=value,
                    cls=cls,
                )
            return factory_classes.default_factory.process(field=field)
        except KeyError as exc:
            raise KeyError(
                f"This attributes type is not supported: {field.type}"
            ) from exc


class EnumClassFactory:
    def process(
        self,
        obj: OpenAPIModel,
        field: Field,
        factory_classes: FactoryClassesInstance,
    ) -> Optional[enum.Enum]:
        """Processing Enum types. This class acts as an adapter for the
        EnumTypeFactory.

        Parameters
        ----------
        obj
            OpenAPIModel instance
        field
            Field object of dataclass attribute
        factory_classes
            FactoryClasses instance which acts as a toolbox of Factory classes

        Returns
        -------
            An enum instance
        """
        return factory_classes.type_factories["enum"].process(
            key=field.name, value=getattr(obj, field.name), cls=field.type
        )


class JsonPatchClassFactory:
    def process(
        self,
        obj: OpenAPIModel,
        field: Field,
        factory_classes: FactoryClassesInstance,
    ) -> Optional[JsonPatch]:
        """Processing JsonPatch types. This class acts as an adapter for the
        JsonPatchTypeFactory.

        Parameters
        ----------
        obj
            OpenAPIModel instance
        field
            Field object of dataclass attribute
        factory_classes
            FactoryClasses instance which acts as a toolbox of Factory classes

        Returns
        -------
            An JsonPatch instance
        """
        return factory_classes.type_factories["json_patch"].process(
            key=field.name, value=getattr(obj, field.name), cls=field.type
        )


class AnyClassFactory:
    def process(
        self,
        obj: OpenAPIModel,
        field: Field,
        factory_classes: FactoryClassesInstance,
    ) -> Any:
        """Processing Any types.

        Parameters
        ----------
        obj
            OpenAPIModel instance
        field
            Field object of dataclass attribute
        factory_classes
            FactoryClasses instance which acts as a toolbox of Factory classes

        Returns
        -------
            Any value
        """
        value = getattr(obj, field.name, None)
        if not value:
            return factory_classes.default_factory.process(field=field)
        return value
