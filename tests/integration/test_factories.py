import sys
from datetime import datetime
from typing import Any

import pytest
from alpha import exceptions
from alpha.factories.request_factory import RequestFactory
from alpha.infra.models.json_patch import JsonPatch
from tests.fixtures._domain_models import Gender, TrackPoint
from tests.fixtures.fake_service_class import FakeService
from tests.integration.fixtures.api_generate_models._test_model import (
    TestModel as ApiTestModel,
)


def test_request_factory(str_func: Any, request_factory_factory: RequestFactory):
    response = request_factory_factory(func=str_func, cast_args=True).__call__(obj=1)
    assert response == "1"


def test_request_factory_generic_types(
    fake_service: FakeService, request_factory_factory: RequestFactory
):
    result = request_factory_factory(
        func=fake_service.simple_types, cast_args=True
    ).__call__(string=123, integer="1", floating_point="1.0", boolean="True")

    assert result["string"] == "123"
    assert result["integer"] == 1
    assert result["floating_point"] == 1.0
    assert result["boolean"]


def test_request_factory_typing_union_generic_alias(
    fake_service: FakeService, request_factory_factory: RequestFactory
):
    result = request_factory_factory(
        func=fake_service.typing_union_generic_alias, cast_args=True
    ).__call__(
        optional_boolean=True,
        optional_any_list=["1", 1, 1.0],
        optional_str_list=["1", 1, 1.0],
        optional_int_list=["123", 12.3],
    )

    assert result["optional_boolean"]
    assert result["optional_any_list"][0] == "1"
    assert result["optional_any_list"][1] == 1
    assert result["optional_any_list"][2] == 1.0
    assert result["optional_str_list"][0] == "1"
    assert result["optional_str_list"][1] == "1"
    assert result["optional_str_list"][2] == "1.0"
    assert result["optional_int_list"][0] == 123
    assert result["optional_int_list"][1] == 12

    result = request_factory_factory(
        func=fake_service.typing_union_generic_alias, cast_args=False
    ).__call__(
        optional_boolean=True,
        optional_any_list=["1", 1, 1.0],
        optional_str_list=["1", 1, 1.0],
        optional_int_list=["123", 12.3],
    )

    assert result["optional_boolean"]
    assert result["optional_any_list"][0] == "1"
    assert result["optional_any_list"][1] == 1
    assert result["optional_any_list"][2] == 1.0
    assert result["optional_str_list"][0] == "1"
    assert result["optional_str_list"][1] == 1
    assert result["optional_str_list"][2] == 1.0
    assert result["optional_int_list"][0] == "123"
    assert result["optional_int_list"][1] == 12.3

    result = request_factory_factory(
        func=fake_service.typing_union_generic_alias, cast_args=False
    ).__call__(
        optional_boolean=None,
        optional_any_list=None,
        optional_str_list=None,
        optional_int_list=None,
    )

    assert result["optional_boolean"] is None
    assert result["optional_any_list"] is None
    assert result["optional_str_list"] is None
    assert result["optional_int_list"] is None


if sys.version_info.minor >= 10:

    def test_request_factory_types_union_type(
        fake_service: FakeService, request_factory_factory: RequestFactory
    ):
        result = request_factory_factory(
            func=fake_service.types_union_type, cast_args=True
        ).__call__(
            optional_boolean=True,
            optional_any_list=["1", 1, 1.0],
            optional_str_list=["1", 1, 1.0],
            optional_int_list=["123", 12.3],
        )

        assert result["optional_boolean"]
        assert result["optional_any_list"][0] == "1"
        assert result["optional_any_list"][1] == 1
        assert result["optional_any_list"][2] == 1.0
        assert result["optional_str_list"][0] == "1"
        assert result["optional_str_list"][1] == "1"
        assert result["optional_str_list"][2] == "1.0"
        assert result["optional_int_list"][0] == 123
        assert result["optional_int_list"][1] == 12

        result = request_factory_factory(
            func=fake_service.types_union_type, cast_args=False
        ).__call__(
            optional_boolean=True,
            optional_any_list=["1", 1, 1.0],
            optional_str_list=["1", 1, 1.0],
            optional_int_list=["123", 12.3],
        )

        assert result["optional_boolean"]
        assert result["optional_any_list"][0] == "1"
        assert result["optional_any_list"][1] == 1
        assert result["optional_any_list"][2] == 1.0
        assert result["optional_str_list"][0] == "1"
        assert result["optional_str_list"][1] == 1
        assert result["optional_str_list"][2] == 1.0
        assert result["optional_int_list"][0] == "123"
        assert result["optional_int_list"][1] == 12.3

        result = request_factory_factory(
            func=fake_service.typing_union_generic_alias, cast_args=False
        ).__call__(
            optional_boolean=None,
            optional_any_list=None,
            optional_str_list=None,
            optional_int_list=None,
        )

        assert result["optional_boolean"] is None
        assert result["optional_any_list"] is None
        assert result["optional_str_list"] is None
        assert result["optional_int_list"] is None


def test_request_factory_factory_list(
    list_func, request_factory_factory: RequestFactory
):
    response = request_factory_factory(func=list_func, cast_args=True).__call__(
        obj=["a", "b", "c"]
    )
    assert response == "abc"

    with pytest.raises(exceptions.ClassMismatchException):
        request_factory_factory(func=list_func, cast_args=True).__call__(obj="abc")


def test_request_factory_factory_enum(
    enum_func, request_factory_factory: RequestFactory
):
    response = request_factory_factory(func=enum_func, cast_args=True).__call__(
        obj="MALE"
    )
    assert isinstance(response, Gender)
    assert response.value == 1


def test_request_factory_factory_json_patch(
    json_patch_func, api_json_patch, request_factory_factory: RequestFactory
):
    response = request_factory_factory(func=json_patch_func, cast_args=True).__call__(
        obj=[api_json_patch]
    )
    assert isinstance(response, JsonPatch)


def test_request_factory_factory_cast_args(
    str_func, request_factory_factory: RequestFactory
):
    response = request_factory_factory(func=str_func, cast_args=True).__call__(obj=1)
    assert response == "1"

    response = request_factory_factory(func=str_func, cast_args=False).__call__(obj=1)
    assert response == 1

    response = request_factory_factory(func=str_func, cast_args=True).__call__(
        obj=datetime(2020, 1, 1, 1, 1, 1)
    )
    assert response == "2020-01-01 01:01:01"


def test_request_factory_factory_dataclass(
    dataclass_func, api_track_point, request_factory_factory: RequestFactory
):
    response = request_factory_factory(func=dataclass_func, cast_args=True).__call__(
        obj=api_track_point
    )
    assert isinstance(response, TrackPoint)


def test_request_response_factory_integration(
    api_test_model: ApiTestModel, request_factory, response_factory
):
    assert api_test_model.single_str == "string"
    assert api_test_model.single_enum == "FIRST"
    assert api_test_model.single_dict.param == "string"
    assert api_test_model.list_of_str == ["string"]
    assert api_test_model.flat_object.text == "string"
    assert api_test_model.list_of_flat_objects[0].text == "string"
    assert api_test_model.nested_object.flat_object.text == "string"
    assert api_test_model.nested_object.list_of_flat_objects[0].text == "string"

    model_instance = request_factory.__call__(test_model=api_test_model)

    assert model_instance.single_dict["param"] == "string"

    result = response_factory.process(response=model_instance, cls=ApiTestModel)

    assert isinstance(result, ApiTestModel)
    assert result.single_str == "string"
    assert result.single_enum == "FIRST"
    assert result.single_dict.param == "string"
    assert result.list_of_str == ["string"]
    assert result.flat_object.text == "string"
    assert result.list_of_flat_objects[0].text == "string"
    assert result.nested_object.flat_object.text == "string"
    assert result.nested_object.list_of_flat_objects[0].text == "string"
