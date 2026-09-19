"""_summary_"""

import pytest

from alpha import exceptions
from alpha.interfaces.factories import ModelClassFactoryInstance
from alpha.interfaces.openapi_model import OpenAPIModel
from tests.fixtures._attrs_models import AttrsAddress
from tests.fixtures._domain_models import Address, ResponseUser
from tests.fixtures._pydantic_models import PydanticAddress


def test_model_class_factory(
    model_class_factory_unit: ModelClassFactoryInstance,
) -> None:
    with pytest.raises(exceptions.ModelClassFactoryException):
        model_class_factory_unit.process(obj="test", cls="test")

    with pytest.raises(exceptions.ModelClassFactoryException):
        model_class_factory_unit.process(obj="test", cls=ResponseUser)


def test_model_class_factory_dataclass(
    api_address: OpenAPIModel,
    model_class_factory_unit: ModelClassFactoryInstance,
) -> None:
    result = model_class_factory_unit.process(obj=api_address, cls=Address)

    assert isinstance(result, Address)
    assert result.street == "type"
    assert result.house_number == 42
    assert result.city == "type"
    assert not hasattr(result, "country")


def test_model_class_factory_attrs(
    api_address: OpenAPIModel,
    model_class_factory_unit: ModelClassFactoryInstance,
) -> None:
    result = model_class_factory_unit.process(
        obj=api_address, cls=AttrsAddress
    )

    assert isinstance(result, AttrsAddress)
    assert result.street == "type"
    assert result.house_number == 42
    assert result.city == "type"
    assert not hasattr(result, "country")


def test_model_class_factory_pydantic(
    api_address: OpenAPIModel,
    model_class_factory_unit: ModelClassFactoryInstance,
) -> None:
    result = model_class_factory_unit.process(
        obj=api_address, cls=PydanticAddress
    )

    assert isinstance(result, PydanticAddress)
    assert result.street == "type"
    assert result.house_number == 42
    assert result.city == "type"
    assert not hasattr(result, "_country")
