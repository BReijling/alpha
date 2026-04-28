"""Contains FactoryClasses dataclass"""

from dataclasses import dataclass

from alpha.interfaces.factories import (
    ClassFactory,
    DefaultFactory,
    ModelClassFactoryInstance,
    TypeFactory,
)


@dataclass
class FactoryClasses:
    """A FactoryClasses instance acts as a toolbox for Factory classes

    This class is exclusively used by the `ModelClassFactory` class for storing
    references to Factory classes, which can be used for creating model
    classes.

    Attributes
    ----------
    class_factories
        A dictionary mapping class names to their corresponding ClassFactory
        instances.
    type_factories
        A dictionary mapping type names to their corresponding TypeFactory
        instances.
    default_factory
        The default factory to use when no specific factory is found.
    model_class_factory
        An optional ModelClassFactoryInstance to use for creating model
        classes.
    """

    class_factories: dict[str, ClassFactory]
    type_factories: dict[str, TypeFactory]
    default_factory: DefaultFactory
    model_class_factory: ModelClassFactoryInstance | None
