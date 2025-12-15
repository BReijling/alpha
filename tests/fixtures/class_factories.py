from datetime import date, datetime

import pytest
from alpha.factories.class_factories import (
    AnyClassFactory,
    DataclassClassFactory,
    DictClassFactory,
    EnumClassFactory,
    GenericAliasClassFactory,
    IterableClassFactory,
    JsonPatchClassFactory,
    NativeClassFactory,
    UnionClassFactory,
)
from alpha.factories.default_field_factory import DefaultFieldFactory
from alpha.factories.model_class_factory import ModelClassFactory
from alpha.factories.models.factory_classes import FactoryClasses
from alpha.interfaces.factories import (
    ClassFactory,
    FactoryClassesInstance,
)
from tests.fixtures._api_classes import (
    ApiTrackModel,
    FakeAddressModel,
    FakeAddressNested,
)
from tests.fixtures.fake_factory_classes import (
    FakeAllTypeClass,
    FakeClassFactory,
    FakeDataclass,
    FakeDefaultFactory,
    FakeDefaultFactoryClass,
    FakeDictFactoryClass,
    FakeModelClassFactory,
    FakeTypeFactory,
)
from tests.fixtures._domain_models import CarType


@pytest.fixture
def factory_classes() -> FactoryClassesInstance:
    return FactoryClasses(
        class_factories={
            "iterable": FakeClassFactory("iterable"),
            "dict": FakeClassFactory("dict"),
            "dataclass": FakeClassFactory("dataclass"),
            "generic_alias": FakeClassFactory("generic_alias"),
            "union": FakeClassFactory("union"),
            "native": FakeClassFactory("native"),
            "enum": FakeClassFactory("enum"),
            "json_patch": FakeClassFactory("json_patch"),
            "any": FakeClassFactory("any"),
        },
        type_factories={
            "generic": FakeTypeFactory("generic"),
            "datetime": FakeTypeFactory("datetime"),
            "enum": FakeTypeFactory("enum"),
            "json_patch": FakeTypeFactory("json_patch"),
        },
        default_factory=FakeDefaultFactory(),
        model_class_factory=FakeModelClassFactory("model"),
    )


@pytest.fixture
def fake_all_type_class():
    return FakeAllTypeClass(
        types_list=["abc"],
        typing_list=["abc"],
        types_tuple=("abc",),
        typing_tuple=("abc",),
        types_set={"abc"},
        typing_set={"abc"},
        types_dict={"abc": "abc"},
        typing_dict={"abc": "abc"},
        types_list_union=["abc"],
        typing_list_union=["abc"],
        enum_list=[CarType.STATION],
        types_union=1,
        types_union2="1",
        typing_union=1,
        optional_list=None,
        optional_dataclass=FakeDataclass("field"),
        no_str=None,
        str_="abc",
        int_="1",
        float_=0.1,
        complex_=complex(1),
        bool_=True,
        date_=date(1, 1, 1),
        datetime_=datetime(2024, 1, 1),
        dataclass_=FakeDataclass("field"),
        list_dataclass=[FakeDataclass("field")],
        no_list_dataclass=FakeDataclass("field"),
        json_patch="json_patch",
    )


@pytest.fixture
def fake_dataclass():
    return FakeDataclass


@pytest.fixture
def model_class_factory():
    return ModelClassFactory()


@pytest.fixture
def model_class_factory_unit():
    return ModelClassFactory(
        typing_classes={type: FakeClassFactory("type")},
        factory_classes=FactoryClasses(
            class_factories=None,
            type_factories=None,
            default_factory=None,
            model_class_factory="not none",
        ),
    )


@pytest.fixture
def fake_model_class_factory():
    return ModelClassFactory(
        typing_classes={type: FakeClassFactory("type")},
        factory_classes=FactoryClasses(
            class_factories=None,
            type_factories=None,
            default_factory=None,
            model_class_factory="not none",
        ),
    )


@pytest.fixture
def generic_alias_class_factory() -> ClassFactory:
    return GenericAliasClassFactory()


@pytest.fixture
def union_class_factory() -> ClassFactory:
    return UnionClassFactory()


@pytest.fixture
def enum_class_factory() -> ClassFactory:
    return EnumClassFactory()


@pytest.fixture
def json_patch_class_factory() -> ClassFactory:
    return JsonPatchClassFactory()


@pytest.fixture
def any_class_factory() -> ClassFactory:
    return AnyClassFactory()


@pytest.fixture
def native_class_factory() -> ClassFactory:
    return NativeClassFactory()


@pytest.fixture
def dataclass_class_factory() -> ClassFactory:
    return DataclassClassFactory()


@pytest.fixture
def dict_class_factory() -> ClassFactory:
    return DictClassFactory()


@pytest.fixture
def iterable_class_factory() -> ClassFactory:
    return IterableClassFactory()


@pytest.fixture
def default_field_factory():
    return DefaultFieldFactory()


@pytest.fixture
def default_fields():
    return getattr(FakeDefaultFactoryClass, "__dataclass_fields__")


@pytest.fixture
def fake_dict_factory_class():
    return FakeDictFactoryClass


@pytest.fixture
def api_address() -> FakeAddressModel:
    return FakeAddressModel(
        street="Avenue de Monte-Carlo", house_number=1, city="Monte Carlo"
    )


@pytest.fixture
def api_address_nested() -> FakeAddressNested:
    return FakeAddressNested(
        address=FakeAddressModel(
            street="Avenue de Monte-Carlo", house_number=1, city="Monte Carlo"
        )
    )


@pytest.fixture
def api_track_model() -> ApiTrackModel:
    return ApiTrackModel()
