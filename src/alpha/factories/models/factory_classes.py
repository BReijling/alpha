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
    """A FactoryClasses instance acts as a toolbox for Factory classes"""

    class_factories: dict[str, ClassFactory]
    type_factories: dict[str, TypeFactory]
    default_factory: DefaultFactory
    model_class_factory: ModelClassFactoryInstance | None
