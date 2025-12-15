import pytest
from alpha import exceptions


def test_query_clause(query_clause):
    assert query_clause.field == "test"

    with pytest.raises(NotImplementedError):
        assert query_clause.query_clause(query=None)

    with pytest.raises(exceptions.InstrumentedAttributeMissing):
        assert query_clause._raise_instrumented_attr_exception()
