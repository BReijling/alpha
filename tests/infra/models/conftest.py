from typing import Any

import pytest

from alpha.infra.models.filter_operators import And, FilterOperator, Or
from alpha.infra.models.query_clause import QueryClause


@pytest.fixture
def fake_query():
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return "fake_query_filtered"

    return FakeQuery()


@pytest.fixture
def patch_with_date() -> list[dict[str, Any]]:
    return [
        {"op": "replace", "path": "/", "value": "string"},
        {"op": "replace", "path": "/", "value": "2015-03-17"},
    ]


@pytest.fixture
def patch_with_datetime() -> list[dict[str, Any]]:
    return [
        {"op": "replace", "path": "/", "value": "string"},
        {"op": "replace", "path": "/", "value": "2015-03-17T13:00:00.000"},
    ]


@pytest.fixture
def patch_without_string() -> list[dict[str, Any]]:
    return [
        {"op": "add", "path": "/", "value": 1},
        {"op": "add", "path": "/", "value": 0.5},
        {"op": "add", "path": "/", "value": {"key": "value"}},
        {"op": "add", "path": "/", "value": ["test"]},
    ]


@pytest.fixture
def patch_with_boolean() -> list[dict[str, Any]]:
    return [
        {"op": "replace", "path": "/", "value": "string"},
        {"op": "replace", "path": "/", "value": "true"},
        {"op": "replace", "path": "/", "value": "false"},
        {"op": "replace", "path": "/", "value": "True"},
        {"op": "replace", "path": "/", "value": "FALSE"},
    ]


@pytest.fixture
def query_clause() -> QueryClause:
    return QueryClause(field="test")


@pytest.fixture
def filter_operator():
    return FilterOperator()


@pytest.fixture
def and_operator():
    return And()


@pytest.fixture
def or_operator():
    return Or()
