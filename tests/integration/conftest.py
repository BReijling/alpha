import os
from datetime import date
from typing import Any

import pytest

from alpha.adapters.sqla_unit_of_work import SqlAlchemyUnitOfWork
from alpha.factories.request_factory import RequestFactory
from alpha.infra.database.sql_alchemy_database import SqlAlchemyDatabase
from alpha.infra.models.json_patch import JsonPatch
from alpha.interfaces.sql_repository import SqlRepository
from alpha.repositories.default_sql_repository import DefaultSqlRepository
from alpha.repositories.models.repository_model import RepositoryModel
from tests.fixtures._domain_models import Gender, TrackPoint
from tests.fixtures.api_generate_models.json_patch import (
    JsonPatch as ApiJsonPatch,
)
from tests.fixtures.class_factories import (
    api_address,
    model_class_factory,
)
from tests.fixtures.fake_service_class import FakeService
from tests.integration.fixtures._test_model import TestModel
from tests.integration.fixtures.api_generate_models._test_model import (
    TestModel as ApiTestModel,
)
from tests.integration.fixtures.api_generate_models._test_model_single_dict import (
    TestModelSingleDict,
)
from tests.integration.fixtures.api_generate_models.flat_object import (
    FlatObject,
)
from tests.integration.fixtures.api_generate_models.nested_object import (
    NestedObject,
)

from tests.integration._classes import FakeMapper, Pet, PetType
from tests.integration._filters import (
    contains_filter,
    endswith_filter,
    eq_filter,
    good_boy_order_desc,
    gt_filter,
    gte_filter,
    icontains_filter,
    iendswith_filter,
    ilike_filter,
    in_filter,
    istartswith_filter,
    like_filter,
    lt_filter,
    lte_filter,
    name_order_asc,
    name_order_desc,
    ncontains_filter,
    nendswith_filter,
    neq_filter,
    nicontains_filter,
    niendswith_filter,
    nilike_filter,
    nin_filter,
    nistartswith_filter,
    nlike_filter,
    nstartswith_filter,
    startswith_filter,
    weight_neq_none_filter,
    weight_order_desc,
    and_filter,
    or_filter,
)


@pytest.fixture
def sqlite_database() -> SqlAlchemyDatabase:
    return SqlAlchemyDatabase(
        conn_str="sqlite:///:memory:",
        create_schema=False,
        db_type="sqlite",
        mapper=FakeMapper,
    )


@pytest.fixture
def mysql_database() -> SqlAlchemyDatabase:
    return SqlAlchemyDatabase(
        host="127.0.0.1",
        port=3306,
        username="root",
        password="mysql",
        db_name="pytest",
        db_type="mysql",
        mapper=FakeMapper,
    )


@pytest.fixture
def psql_database() -> SqlAlchemyDatabase:
    return SqlAlchemyDatabase(
        host=os.getenv("TEST_PSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("TEST_PSQL_PORT", "5432")),
        username=os.getenv("TEST_PSQL_USERNAME", "postgres"),
        password=os.getenv("TEST_PSQL_PASSWORD", "postgres"),
        db_name=os.getenv("TEST_PSQL_DATABASE", "postgres"),
        db_type="postgresql",
        mapper=FakeMapper,
    )


# @pytest.fixture(
#     params=["sqlite_database", "mysql_database", "psql_database"],
#     ids=["sqlite", "mysql", "postgresql"],
# )
# @pytest.fixture(
#     params=["sqlite_database", "psql_database"],
#     ids=["sqlite", "postgresql"],
# )
@pytest.fixture(
    params=[
        "sqlite_database",
    ],
    ids=[
        "sqlite",
    ],
)
def uow(request) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(
        db=request.getfixturevalue(request.param),
        repos=[
            RepositoryModel(
                name="pets",
                repository=DefaultSqlRepository[Pet],
                default_model=Pet,
                interface=SqlRepository,
            )
        ],
    )


@pytest.fixture
def pet() -> Pet:
    return Pet(
        id=999,
        name="PetName",
        pet_type=PetType.DOG,
        good_boy=True,
        date_of_birth=date(2020, 1, 1),
    )


@pytest.fixture
def pets() -> list[Pet]:
    return [
        Pet(
            id=1,
            name="Max",
            pet_type=PetType.DOG,
            good_boy=True,
            date_of_birth=date(2015, 1, 1),
            weight=12.7,
            remarks="Max is a really good boy!",
        ),
        Pet(
            id=2,
            name="Pluto",
            pet_type=PetType.DOG,
            good_boy=True,
            date_of_birth=date(1930, 1, 1),
            weight=18.2,
            remarks="Pluto is the loyal four-legged friend of Mickey Mouse.",
        ),
        Pet(
            id=3,
            name="Tom",
            pet_type=PetType.CAT,
            good_boy=False,
            date_of_birth=date(1940, 1, 1),
            weight=8.5,
            remarks="Jerry always outsmarts Tom",
        ),
        Pet(
            id=4,
            name="Bugs",
            pet_type=PetType.RABBIT,
            date_of_birth=date(1938, 1, 1),
            remarks="What's up doc?",
        ),
        Pet(
            id=5,
            name="Daffy",
            pet_type=PetType.DUCK,
            date_of_birth=date(1937, 1, 1),
        ),
    ]


@pytest.fixture
def api_flat_object():
    obj = FlatObject()
    return obj


@pytest.fixture
def api_nested_object(api_flat_object: FlatObject):
    obj = NestedObject(
        flat_object=api_flat_object,
        list_of_flat_objects=[api_flat_object],
    )
    return obj


@pytest.fixture
def single_dict_object():
    obj = TestModelSingleDict()
    return obj


@pytest.fixture
def api_test_model(
    api_flat_object: FlatObject,
    api_nested_object: NestedObject,
    single_dict_object: TestModelSingleDict,
):
    obj = ApiTestModel(
        single_date="2000-01-01",
        single_datetime="2000-01-01T12:34:56",
        single_dict=single_dict_object,
        flat_object=api_flat_object,
        nested_object=api_nested_object,
        list_of_flat_objects=[api_flat_object],
        list_of_nested_objects=[api_nested_object],
        list_of_str=["string"],
        list_of_int=[123],
        list_of_float=[123.45],
        tuple_of_str=["string"],
        tuple_of_int=[123],
        tuple_of_float=[123.45],
        set_of_str=["string"],
        set_of_int=[123],
        set_of_float=[123.45],
    )
    return obj


@pytest.fixture
def api_json_patch():
    return ApiJsonPatch(op="add", path="/test", value="test")


@pytest.fixture
def request_factory_factory():
    def factory(
        func: Any,
        cast_args: bool,
        use_model_class_factory: bool = True,
    ):
        return RequestFactory(
            func=func,
            cast_args=cast_args,
            use_model_class_factory=use_model_class_factory,
        )

    return factory


@pytest.fixture
def request_factory():
    def func(test_model: TestModel):
        return test_model

    return RequestFactory(func=func)


@pytest.fixture
def str_func():
    def func(obj: str):
        return obj

    return func


@pytest.fixture
def list_func():
    def func(obj: list[str]):
        return "".join(obj)

    return func


@pytest.fixture
def enum_func():
    def func(obj: Gender):
        return obj

    return func


@pytest.fixture
def dataclass_func():
    def func(obj: TrackPoint):
        return obj

    return func


@pytest.fixture
def json_patch_func():
    def func(obj: JsonPatch):
        return obj

    return func


@pytest.fixture
def fake_service():
    return FakeService()
