from dataclasses import (
    dataclass as native_dataclass,
)

from attrs import define

from pydantic import BaseModel
from pydantic.dataclasses import (
    dataclass as pydantic_dataclass,
)
import pytest


from alpha.domain.models.base_model import BaseDomainModel
from alpha.domain.models.permission import Permission
from alpha.domain.models.user import User
from alpha.domain.models.group import Group


@native_dataclass(slots=True)
class NativeDataClass(BaseDomainModel):
    id: int
    string: str
    integer: int = 0
    optional_float: float | None = None


@define
class AttrsClass(BaseDomainModel):
    id: int
    string: str
    integer: int = 0
    optional_float: float | None = None


@pydantic_dataclass
class PydanticDataClass(BaseDomainModel):
    id: int
    string: str
    integer: int = 0
    optional_float: float | None = None


class PydanticModel(BaseModel, BaseDomainModel):
    id: int
    string: str
    integer: int = 0
    optional_float: float | None = None


class AnotherDataModel(BaseDomainModel):
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


class AnotherDataModelWithSlots(BaseDomainModel):
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
def sample_user():
    return User(username="sampleuser", email="sampleuser@example.com")


@pytest.fixture
def another_sample_user():
    return User(
        username="anotheruser",
        email="anotheruser@example.com",
        groups=["group1"],
        permissions=["read"],
    )


@pytest.fixture
def sample_group():
    return Group(name="samplegroup")


@pytest.fixture
def another_sample_group():
    return Group(name="anothergroup", description="Another sample group")


@pytest.fixture
def sample_permission():
    return Permission(name="read")


@pytest.fixture
def another_sample_permission():
    return Permission(name="write", description="Allows writing data")
