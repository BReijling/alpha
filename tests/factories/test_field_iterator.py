from dataclasses import _MISSING_TYPE

from pydantic_core import PydanticUndefined
import pytest
from alpha.factories.field_iterator import Field, FieldIterator
from tests.fixtures._attrs_models import AttrsAddressIncorrectType


def test_field(field):
    assert field.type == str
    assert str(field).startswith("Field(")

    with pytest.raises(NameError):
        Field(init=True, name="test", type_="Type", default=None)


def test_field_iterator():
    with pytest.raises(TypeError):
        FieldIterator(None)
    with pytest.raises(NameError):
        FieldIterator(AttrsAddressIncorrectType)


def test_field_iterator_dataclass(field_iterator_dataclass):
    assert iter(field_iterator_dataclass)

    field = next(field_iterator_dataclass)
    assert isinstance(field, Field)
    assert not isinstance(field.type, str)
    assert isinstance(field.default_factory, _MISSING_TYPE)


def test_field_iterator_attrs(field_iterator_attrs):
    assert iter(field_iterator_attrs)

    field = next(field_iterator_attrs)
    assert isinstance(field, Field)
    assert not isinstance(field.type, str)
    assert field.default_factory == None


def test_field_iterator_pydantic(field_iterator_pydantic):
    assert iter(field_iterator_pydantic)

    field = next(field_iterator_pydantic)
    assert isinstance(field, Field)
    assert not isinstance(field.type, str)
    assert field.default is PydanticUndefined
