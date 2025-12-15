"""_summary_"""

from typing import Any

import pytest

from alpha import exceptions
from alpha.factories.request_factory import RequestFactory
from tests.fixtures._api_classes import ApiTrack


def test_request_factory(str_func: Any, request_factory: RequestFactory):
    response = request_factory(func=str_func, cast_args=True).__call__(obj=None)
    assert response == "FakeTypeFactory"


def test_request_factory_list(list_func, request_factory: RequestFactory):
    response = request_factory(func=list_func, cast_args=True).__call__(obj=["a"])
    assert response == ["FakeTypeFactory"]

    with pytest.raises(exceptions.ClassMismatchException):
        request_factory(func=list_func, cast_args=True).__call__(obj="abc")


def test_request_factory_enum(enum_func, request_factory: RequestFactory):
    response = request_factory(func=enum_func, cast_args=True).__call__(obj=None)
    assert response == "FakeTypeFactory"


def test_request_factory_json_patch(json_patch_func, request_factory: RequestFactory):
    response = request_factory(func=json_patch_func, cast_args=True).__call__(obj=None)
    assert response == "FakeTypeFactory"


def test_request_factory_cast_args(str_func, request_factory: RequestFactory):
    response = request_factory(func=str_func, cast_args=True).__call__(obj=None)
    assert response == "FakeTypeFactory"


def test_request_factory_dataclass(
    dataclass_func, api_track_point: ApiTrack, request_factory: RequestFactory
):
    response = request_factory(
        func=dataclass_func, cast_args=True, use_model_class_factory=False
    ).__call__(obj=api_track_point)
    assert isinstance(response, ApiTrack)
