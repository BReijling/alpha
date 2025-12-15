"""_summary_"""

import pytest
from alpha import exceptions
from alpha.factories.model_class_factory import ModelClassFactory

from tests.fixtures._attrs_models import AttrsAddress
from tests.fixtures._domain_models import Address


def test_model_class_factory(api_address, model_class_factory: ModelClassFactory):
    """_summary_"""
    address = model_class_factory.process(api_address, Address)
    assert isinstance(address, Address)
    assert isinstance(address.city, str)
    assert isinstance(address.house_number, int)

    address = model_class_factory.process(api_address, AttrsAddress)
    assert isinstance(address, AttrsAddress)
    assert isinstance(address.city, str)
    assert isinstance(address.house_number, int)

    with pytest.raises(exceptions.ModelClassFactoryException):
        model_class_factory.process(obj="test", cls="test")
