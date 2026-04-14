from typing import Any

import pytest

from alpha.adapters.rest_api_unit_of_work import RestApiUnitOfWork
from alpha.adapters.sqla_unit_of_work import SqlAlchemyUnitOfWork
from alpha.infra.databases.sql_alchemy import SqlAlchemyDatabase
from alpha.interfaces.api_repository import ApiRepository
from alpha.repositories.models.repository_model import RepositoryModel
from tests.fixtures._domain_models import TestModel
from tests.fixtures.fake_uow_repositories import FakeRepository


class InvalidRepository:
    def __init__(self, session, default_model):
        pass


@pytest.fixture
def test_database():
    return SqlAlchemyDatabase(
        conn_str="sqlite:///:memory:",
        create_schema=False,
        create_tables=False,
    )


@pytest.fixture
def repo_model() -> RepositoryModel[Any]:
    return RepositoryModel(
        name="test_repo",
        repository=FakeRepository,
        default_model=TestModel,
        interface=ApiRepository,
        additional_config=None,
    )


@pytest.fixture
def invalid_repo_model() -> RepositoryModel[Any]:
    return RepositoryModel(
        name="invalid_repo",
        repository=InvalidRepository,
        default_model=None,
        interface=ApiRepository,
        additional_config=None,
    )


@pytest.fixture
def sql_alchemy_uow(repo_model, test_database) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(db=test_database, repos=[repo_model])


@pytest.fixture
def sql_alchemy_uow_with_invalid_repo(
    invalid_repo_model, test_database
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(db=test_database, repos=[invalid_repo_model])


@pytest.fixture
def rest_api_uow(repo_model) -> RestApiUnitOfWork:
    return RestApiUnitOfWork(repos=[repo_model])


@pytest.fixture
def rest_api_uow_with_invalid_repo(invalid_repo_model) -> RestApiUnitOfWork:
    return RestApiUnitOfWork(repos=[invalid_repo_model])
