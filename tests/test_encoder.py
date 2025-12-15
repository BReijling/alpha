import json
from datetime import date, datetime, time, timezone
from enum import Enum
from typing import Any, Type, TypeVar
from uuid import UUID

import numpy as np
import pandas as pd
import pytest
from alpha.encoder import JSONEncoder

T = TypeVar("T")


@pytest.fixture
def encoder_factory():
    def run_encoder(obj: Any, key: str):
        json_ = json.dumps(obj, cls=JSONEncoder)
        dict_ = json.loads(json_)
        return dict_[key]

    return run_encoder


class FakeOpenAPIModel:
    openapi_types: dict[str, Any]
    attribute_map: dict[str, str]

    def __init__(self, value: str):  # noqa: E501
        self.openapi_types = {"value": str}

        self.attribute_map = {"value": "value"}

        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @classmethod
    def from_dict(cls: Type[T], dikt) -> T:
        pass

    def to_dict(self) -> dict:
        return {}

    def to_str(self) -> str:
        return ""

    def __repr__(self) -> str:
        return ""

    def __eq__(self, other: Any) -> bool:
        return True

    def __ne__(self, other: Any) -> bool:
        return True


class FakeEnum(Enum):
    VALUE = 1


class FakeModelToDict:
    def to_dict(self):
        return {"a": 1}


class FakeModelToList:
    def to_list(self):
        return [1, 2, 3]


@pytest.fixture
def uuid_str():
    return "af6b2857-567c-490b-81e6-db21dbeba69b"


@pytest.fixture
def obj(uuid_str) -> dict[str, Any]:
    return {
        "datetime": datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        "date": date(2000, 1, 1),
        "time": time(1, 2, 3),
        "pd_timestamp": pd.to_datetime("2000-01-01"),
        "np_int64": np.int64(1),
        "np_float32": np.float32(1.0),
        "enum": FakeEnum.VALUE,
        "set": {1, 2, 3},
        "uuid": UUID(uuid_str),
        "to_dict": FakeModelToDict(),
        "to_list": FakeModelToList(),
        "list": [FakeModelToList()],
        "open_api_model": FakeOpenAPIModel(value="abc"),
        "open_api_model_list": [FakeOpenAPIModel(value="abc")],
    }


def test_datetime(encoder_factory, obj):
    value = encoder_factory(obj, "datetime")
    assert value == "2000-01-01T00:00:00+00:00"


def test_date(encoder_factory, obj):
    value = encoder_factory(obj, "date")
    assert value == "2000-01-01"


def test_time(encoder_factory, obj):
    value = encoder_factory(obj, "time")
    assert value == "01:02:03"


def test_pd_timestamp(encoder_factory, obj):
    value = encoder_factory(obj, "pd_timestamp")
    assert value == "2000-01-01T00:00:00"


def test_np_int64(encoder_factory, obj):
    value = encoder_factory(obj, "np_int64")
    assert value == 1


def test_np_float32(encoder_factory, obj):
    value = encoder_factory(obj, "np_float32")
    assert value == 1.0


def test_enum(encoder_factory, obj):
    value = encoder_factory(obj, "enum")
    assert value == "VALUE"


def test_set(encoder_factory, obj):
    value = encoder_factory(obj, "set")
    assert value == [1, 2, 3]


def test_uuid(encoder_factory, obj, uuid_str):
    value = encoder_factory(obj, "uuid")
    assert value == uuid_str


def test_to_dict(encoder_factory, obj):
    value = encoder_factory(obj, "to_dict")
    assert value == {"a": 1}


def test_to_list(encoder_factory, obj):
    value = encoder_factory(obj, "to_list")
    assert value == [1, 2, 3]


def test_list(encoder_factory, obj):
    value = encoder_factory(obj, "list")
    assert value == [[1, 2, 3]]


def test_open_api_model(encoder_factory, obj):
    value = encoder_factory(obj, "open_api_model")
    assert value == {"value": "abc"}


def test_open_api_model_list(encoder_factory, obj):
    value = encoder_factory(obj, "open_api_model_list")
    assert value == [{"value": "abc"}]
