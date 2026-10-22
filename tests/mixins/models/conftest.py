from dataclasses import dataclass
from typing import Any

from attrs import define

from pydantic import BaseModel
from pydantic.dataclasses import (
    dataclass as pydantic_dataclass,
)
import pytest

from alpha.mixins.models.from_dict import FromDictMixin
from alpha.mixins.models.patchable import PatchableMixin
from alpha.mixins.models.to_dict import ToDictMixin
from alpha.mixins.models.updatable import UpdatableMixin


class FakeModel(UpdatableMixin, PatchableMixin):
    @property
    def __patch_fields__(self) -> list[str]:
        return ["name", "description", "collection"]

    @property
    def __update_fields__(self) -> list[str]:
        return ["name", "description"]

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.collection = []
        self.modified_at = None
        self.updated_at = None


class AnotherFakeModel(UpdatableMixin, PatchableMixin):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


@pytest.fixture
def fake_model():
    return FakeModel("name", "description")


@pytest.fixture
def updated_fake_model():
    obj = FakeModel("updated name", "updated description")
    return obj


@pytest.fixture
def another_fake_model():
    return AnotherFakeModel("another name", "another description")


@pytest.fixture
def patch_replace_name():
    return {"op": "replace", "path": "/name", "value": "replaced name"}


@pytest.fixture
def patch_replace_description():
    return {
        "op": "replace",
        "path": "/description",
        "value": "replaced description",
    }


@pytest.fixture
def patch_add_name():
    return {"op": "add", "path": "/name", "value": "added name"}


@pytest.fixture
def patch_add_description():
    return {
        "op": "add",
        "path": "/description",
        "value": "added description",
    }


@pytest.fixture
def patch_remove_name():
    return {"op": "remove", "path": "/name"}


@pytest.fixture
def patch_remove_description():
    return {
        "op": "remove",
        "path": "/description",
    }


@pytest.fixture
def patch_add_to_collection():
    return {"op": "add", "path": "/collection", "value": "item"}


@pytest.fixture
def patch_remove_from_collection():
    return {"op": "remove", "path": "/collection", "value": "item"}


@dataclass(slots=True)
class NativeDataClass(ToDictMixin, FromDictMixin):
    id: int
    string: str
    integer: int = 0
    optional_float: float | None = None


@define
class AttrsClass(ToDictMixin):
    id: int
    string: str
    integer: int = 0
    optional_float: float | None = None


@pydantic_dataclass
class PydanticDataClass(ToDictMixin):
    id: int
    string: str
    integer: int = 0
    optional_float: float | None = None


class PydanticModel(BaseModel, ToDictMixin):
    id: int
    string: str
    integer: int = 0
    optional_float: float | None = None


class AnotherDataModel(ToDictMixin):
    def __init__(
        self,
        id: int | None = None,
        string: str = "",
        integer: int = 0,
        optional_float: float | None = None,
    ):
        self._id = id
        self.string = string
        self.integer = integer
        self.optional_float = optional_float


class AnotherDataModelWithSlots(ToDictMixin):
    __slots__ = ("id", "string", "integer", "optional_float")

    def __init__(
        self,
        id: int | None = None,
        string: str = "",
        integer: int = 0,
        optional_float: float | None = None,
    ):
        self.id = id
        self.string = string
        self.integer = integer
        self.optional_float = optional_float


@pytest.fixture
def native_data_class():
    return NativeDataClass(
        id=0,
        string="sample string",
        integer=42,
        optional_float=3.14,
    )


@pytest.fixture
def attrs_class():
    return AttrsClass(
        id=0,
        string="sample string",
        integer=42,
        optional_float=3.14,
    )


@pytest.fixture
def pydantic_data_class():
    return PydanticDataClass(
        id=0,
        string="sample string",
        integer=42,
        optional_float=3.14,
    )


@pytest.fixture
def pydantic_model():
    return PydanticModel(
        id=0,
        string="sample string",
        integer=42,
        optional_float=3.14,
    )


@pytest.fixture
def another_data_model():
    return AnotherDataModel(
        id=None,
        string="sample string",
        integer=42,
        optional_float=3.14,
    )


@pytest.fixture
def another_data_model_with_slots():
    return AnotherDataModelWithSlots(
        id=None,
        string="sample string",
        integer=42,
        optional_float=3.14,
    )


@pytest.fixture
def native_data_class_dict() -> dict[str, Any]:
    return {
        "id": 0,
        "string": "sample string",
        "integer": 42,
        "optional_float": 3.14,
    }
