"""This module contains the following interfaces:
- ClassFactory
- TypeFactory
- DefaultFactory
- FactoryClassesInstance
"""

from alpha.factories.field_iterator import Field
from typing import Any, Protocol

from alpha.interfaces.attrs_instance import AttrsInstance
from alpha.interfaces.dataclass_instance import DataclassInstance
from alpha.interfaces.openapi_model import OpenAPIModel


class ClassFactory(Protocol):
    """ClassFactory interface

    A ClassFactory implementation only has a 'process' method.
    """

    def process(
        self,
        obj: OpenAPIModel,
        field: Field,
        factory_classes: "FactoryClassesInstance",
    ) -> Any:
        """This method handles the class operation

        Parameters
        ----------
        obj
            Instance of an OpenAPIModel class
        field
            Dataclass field of the destination attribute
        factory_classes
            FactoryClasses instance which acts as a toolbox of Factory classes

        Returns
        -------
            Any object that will be returned by one of the factory classes
            which is called by a ClassFactory implementation
        """


class TypeFactory(Protocol):
    """TypeFactory interface

    A TypeFactory implementation only has a 'process' method.
    """

    def process(
        self, key: str, value: Any, cls: Any, **kwargs: dict[str, Any]
    ) -> Any:
        """This method handles the type operation

        Parameters
        ----------
        key
            Key name
        value
            Source value which corresponds to the factory implementation
        cls
            Class of the destination type
        kwargs
            Additional parameters

        Returns
        -------
            Mapped instance of the value
        """


class DefaultFactory(Protocol):
    """DefaultFactory interface

    A DefaultFactory implementation only has a 'process' method.
    """

    def process(
        self,
        field: Field,
    ) -> Any: ...


class ModelClassFactoryInstance(Protocol):
    """ModelClassFactory dataclass interface"""

    def process(
        self,
        obj: OpenAPIModel,
        cls: DataclassInstance | AttrsInstance | Any,
    ) -> DataclassInstance | AttrsInstance | None: ...


class FactoryClassesInstance(Protocol):
    """FactoryClasses dataclass interface"""

    class_factories: dict[str, ClassFactory]
    type_factories: dict[str, TypeFactory]
    default_factory: DefaultFactory
    model_class_factory: ModelClassFactoryInstance | None
