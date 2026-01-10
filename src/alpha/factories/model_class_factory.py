"""Contains ModelClassFactory class"""

import enum
import types
import typing
from typing import Any

from alpha import exceptions
from alpha.factories.class_factories import (
    AnyClassFactory,
    DataclassClassFactory,
    DictClassFactory,
    EnumClassFactory,
    GenericAliasClassFactory,
    IterableClassFactory,
    NativeClassFactory,
    UnionClassFactory,
)
from alpha.factories.default_field_factory import DefaultFieldFactory
from alpha.factories.field_iterator import FieldIterator
from alpha.factories.models.factory_classes import FactoryClasses
from alpha.factories.type_factories import (
    GenericTypeFactory,
    DatetimeTypeFactory,
    EnumTypeFactory,
    JsonPatchTypeFactory,
)
from alpha.interfaces.attrs_instance import AttrsInstance
from alpha.interfaces.dataclass_instance import DataclassInstance
from alpha.interfaces.factories import (
    ClassFactory,
    TypeFactory,
)
from alpha.interfaces.openapi_model import OpenAPIModel
from alpha.interfaces.pydantic_instance import PydanticInstance
from alpha.utils.version_check import minor_version_gte


CLASS_FACTORIES: dict[str, ClassFactory] = {
    "iterable": IterableClassFactory(),
    "dict": DictClassFactory(),
    "dataclass": DataclassClassFactory(),
    "generic_alias": GenericAliasClassFactory(),
    "union": UnionClassFactory(),
    "native": NativeClassFactory(),
    "enum": EnumClassFactory(),
    "any": AnyClassFactory(),
}


TYPE_FACTORIES: dict[str, TypeFactory] = {
    "generic": GenericTypeFactory(),
    "datetime": DatetimeTypeFactory(),
    "enum": EnumTypeFactory(),
    "json_patch": JsonPatchTypeFactory(),
}


TYPING_CLASSES: dict[object, ClassFactory] = {
    getattr(typing, "_GenericAlias"): CLASS_FACTORIES["generic_alias"],
    getattr(typing, "_UnionGenericAlias"): CLASS_FACTORIES["union"],
    getattr(typing, "_SpecialForm"): CLASS_FACTORIES["any"],
    enum.EnumMeta: CLASS_FACTORIES["enum"],
    type: CLASS_FACTORIES["native"],
}

if minor_version_gte(10):
    TYPING_CLASSES.update(
        {
            getattr(types, "UnionType"): CLASS_FACTORIES["union"],
        }
    )

if minor_version_gte(11):
    TYPING_CLASSES.update(
        {
            getattr(typing, "_AnyMeta"): CLASS_FACTORIES["any"],
            getattr(types, "GenericAlias"): CLASS_FACTORIES["generic_alias"],
            getattr(enum, "EnumType"): CLASS_FACTORIES["enum"],
        }
    )


FACTORY_CLASSES = FactoryClasses(
    class_factories=CLASS_FACTORIES,
    type_factories=TYPE_FACTORIES,
    default_factory=DefaultFieldFactory(),
    model_class_factory=None,
)


class ModelClassFactory:
    """The ModelClassFactory can be used to cast OpenAPIModel objects to
    instances of dataclass or attrs classes
    """

    def __init__(
        self,
        typing_classes: dict[object, ClassFactory] = TYPING_CLASSES,
        factory_classes: FactoryClasses = FACTORY_CLASSES,
    ) -> None:
        """Initializing and setting the self.typing_classes class variable
        which contains typing classes and references to the corresponding
        factory classes. The set of typing classes depend on the python minor
        version.

        Parameters
        ----------
        typing_classes, optional
            A collection of class types, by default TYPING_CLASSES
        factory_classes, optional
            An instance of FactoryClasses which acts as a toolbox of Factory
            classes, by default FACTORY_CLASSES
        """
        self.typing_classes = typing_classes
        self.factory_classes = factory_classes

        if self.factory_classes.model_class_factory is None:
            self.factory_classes.model_class_factory = self  # type: ignore

    def process(
        self,
        obj: OpenAPIModel,
        cls: DataclassInstance | AttrsInstance | PydanticInstance | Any,
    ) -> DataclassInstance | AttrsInstance | PydanticInstance | None:
        """Creating a new cls instance from a OpenAPIModel object. This class
        uses a compatibele ClassFactory, from the self.typing_classes
        collection, per cls field to process each value.

        Parameters
        ----------
        obj
            OpenAPIModel object
        cls
            A dataclass, attrs, or pydantic class to create a new instance

        Returns
        -------
            Dataclass, attrs, or pydantic instance
        Raises
        ------
        exceptions.ModelClassFactoryException
            When cls is not a dataclass, attrs, or pydantic decorated class
        KeyError
            When the class type is not present in self.typing_classes
        """

        try:
            fields = FieldIterator(cls)
        except TypeError:

            raise exceptions.ModelClassFactoryException(
                "cls argument has to be a dataclass or attrs decorated class"
            )

        params: dict[str, Any] = {}

        for field in [f for f in fields if f.init]:
            type_class: type | str = "Unknown"
            try:
                type_class = field.type.__class__
                class_factory = self.typing_classes[type_class]
                value: Any = class_factory.process(
                    obj=obj,
                    field=field,
                    factory_classes=self.factory_classes,
                )
            except KeyError as exc:
                raise exceptions.ModelClassFactoryException(
                    "The class of this dataclass field is not supported. "
                    f"{field.name=}; "
                    f"{field.type=}; "
                    f"{field.type.__class__=}; "
                ) from exc
            params[field.name] = value
        return cls(**params)
