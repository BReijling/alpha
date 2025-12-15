from datetime import date, datetime, timedelta, timezone

import pytest

from alpha import exceptions
from alpha.infra.models.json_patch import JsonPatch
from alpha.interfaces.factories import TypeFactory
from tests.fixtures._domain_models import CarType, Gender


def test_generic_type_factory(generic_type_factory: TypeFactory):
    """_summary_"""
    assert generic_type_factory.process(key=None, value="string", cls=str) == "string"

    with pytest.raises(exceptions.ObjectConversionNotAllowed):
        generic_type_factory.process(key=None, value="string", cls=dict)
    with pytest.raises(exceptions.ObjectConversionNotSupported):
        generic_type_factory.process(key=None, value="string", cls=object)
    with pytest.raises(exceptions.ObjectConversionError):
        generic_type_factory.process(key=None, value="string", cls=int)


def test_datetime_type_factory(datetime_type_factory: TypeFactory):
    """_summary_"""
    assert datetime_type_factory.process(key=None, value="string", cls=str) == "string"
    assert datetime_type_factory.process(
        key=None, value=datetime(1, 1, 1), cls=datetime
    ) == datetime(1, 1, 1)

    assert datetime_type_factory.process(
        key=None, value="2020-01-12T00:00:00", cls=datetime
    ) == datetime(2020, 1, 12, 0, 0)
    assert datetime_type_factory.process(
        key=None, value="2020-01-12T00:00:00", cls=datetime, day_first=True
    ) == datetime(2020, 12, 1, 0, 0)
    assert datetime_type_factory.process(
        key=None, value="2020-01-12T00:00:00Z", cls=datetime
    ) == datetime(2020, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert datetime_type_factory.process(
        key=None, value="2020-01-12T00:00:00+00:00", cls=datetime
    ) == datetime(2020, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert datetime_type_factory.process(
        key=None, value="2020-01-12T00:00:00+02:00", cls=datetime
    ) == datetime(2020, 1, 12, 0, 0, tzinfo=timezone(timedelta(seconds=7200)))
    assert datetime_type_factory.process(
        key=None, value="2020-01-12T00:00:00", cls=date
    ) == date(2020, 1, 12)
    assert datetime_type_factory.process(
        key=None, value="2020-01-12", cls=datetime
    ) == datetime(2020, 1, 12)


def test_enum_type_factory(enum_type_factory: TypeFactory):
    """_summary_"""
    assert (
        enum_type_factory.process(key="test", value="SEDAN", cls=CarType)
        == CarType.SEDAN
    )
    assert enum_type_factory.process(key="test", value=1, cls=CarType) == CarType.SEDAN
    assert (
        enum_type_factory.process(key="test", value=None, cls=CarType) == CarType.NONE
    )
    assert enum_type_factory.process(key="test", value=None, cls=Gender) is None

    with pytest.raises(AttributeError):
        enum_type_factory.process(key="test", value="CABRIO", cls=CarType)


def test_json_patch_type_factory(
    json_patch_type_factory: TypeFactory,
    api_json_patch_add,
    api_json_patch_replace,
    api_json_patch_remove,
):

    result = json_patch_type_factory.process(
        key="test",
        value=[
            api_json_patch_add,
            api_json_patch_replace,
            api_json_patch_remove,
        ],
        cls=JsonPatch,
    )
    assert isinstance(result, JsonPatch)
    assert result.patch[0]["op"] == "add"
    assert result.patch[1]["op"] == "replace"
    assert result.patch[2]["op"] == "remove"

    with pytest.raises(AttributeError):
        # value is not iterable
        json_patch_type_factory.process(key="test", value="test", cls="test")

        # value has no items
        json_patch_type_factory.process(key="test", value=[], cls="test")

        # value item is not of type OpenAPIModel
        json_patch_type_factory.process(key="test", value=["test"], cls="test")
