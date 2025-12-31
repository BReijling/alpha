from typing import Iterable

import pytest
from sqlalchemy.sql.expression import and_, or_


def test_filter_operator(filter_operator):
    with pytest.raises(NotImplementedError):
        filter_operator.filter_operator


def test_and_operator(and_operator, fake_query):
    assert isinstance(and_operator.search_filters, Iterable)
    assert and_operator.filter_operator == and_

    assert and_operator.filter(query=fake_query) == 'fake_query_filtered'


def test_or_operator(or_operator, fake_query):
    assert isinstance(or_operator.search_filters, Iterable)
    assert or_operator.filter_operator == or_

    assert or_operator.filter(query=fake_query) == 'fake_query_filtered'
