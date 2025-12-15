import pytest
from alpha.factories.type_factories import (
    DatetimeTypeFactory,
    EnumTypeFactory,
    GenericTypeFactory,
    JsonPatchTypeFactory,
)
from alpha.interfaces.factories import (
    TypeFactory,
)


@pytest.fixture
def generic_type_factory() -> TypeFactory:
    return GenericTypeFactory()


@pytest.fixture
def datetime_type_factory() -> TypeFactory:
    return DatetimeTypeFactory()


@pytest.fixture
def enum_type_factory() -> TypeFactory:
    return EnumTypeFactory()


@pytest.fixture
def json_patch_type_factory() -> TypeFactory:
    return JsonPatchTypeFactory()
