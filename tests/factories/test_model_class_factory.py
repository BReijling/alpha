"""_summary_"""

import pytest

from alpha import exceptions
from alpha.interfaces.factories import ModelClassFactoryInstance
from alpha.interfaces.openapi_model import OpenAPIModel
from tests.fixtures._attrs_models import AttrsAddress
from tests.fixtures._domain_models import Address, ResponseUser


def test_model_class_factory(
    api_address: OpenAPIModel,
    model_class_factory_unit: ModelClassFactoryInstance,
) -> None:
    result = model_class_factory_unit.process(obj=api_address, cls=Address)

    keys = ["street", "house_number", "city"]

    assert all([getattr(result, k) == "type" for k in keys])

    result = model_class_factory_unit.process(obj=api_address, cls=AttrsAddress)

    assert all([getattr(result, k) == "type" for k in keys])

    with pytest.raises(exceptions.ModelClassFactoryException):
        model_class_factory_unit.process(obj="test", cls="test")

    with pytest.raises(exceptions.ModelClassFactoryException):
        model_class_factory_unit.process(obj="test", cls=ResponseUser)
