import pytest

from alpha.infra.models.filter_operators import And, Or
from alpha.infra.models.order_by import OrderBy, Order
from alpha.infra.models.search_filter import SearchFilter, Operator

from ._classes import Pet


@pytest.fixture
def lt_filter():
    return SearchFilter(op=Operator.LT, field="weight", value=18.2)


@pytest.fixture
def lte_filter():
    return SearchFilter(op=Operator.LTE, field="weight", value=18.2)


@pytest.fixture
def eq_filter():
    return SearchFilter(op=Operator.EQ, field=Pet.name, value="Daffy")


@pytest.fixture
def neq_filter():
    return SearchFilter(op=Operator.NEQ, field=Pet.name, value="Daffy")


@pytest.fixture
def gt_filter():
    return SearchFilter(op=Operator.GT, field="weight", value=8.5)


@pytest.fixture
def gte_filter():
    return SearchFilter(op=Operator.GTE, field="weight", value=8.5)


@pytest.fixture
def in_filter():
    return SearchFilter(op=Operator.IN, field=Pet.name, value=["Max", "Bugs"])


@pytest.fixture
def nin_filter():
    return SearchFilter(op=Operator.NIN, field=Pet.name, value=["Max", "Bugs"])


@pytest.fixture
def like_filter():
    return SearchFilter(op=Operator.LIKE, field="remarks", value="Jerry%")


@pytest.fixture
def nlike_filter():
    return SearchFilter(op=Operator.NLIKE, field="remarks", value="Jerry%")


@pytest.fixture
def ilike_filter():
    return SearchFilter(op=Operator.ILIKE, field="remarks", value="jerry%")


@pytest.fixture
def nilike_filter():
    return SearchFilter(op=Operator.NILIKE, field="remarks", value="jerry%")


@pytest.fixture
def startswith_filter():
    return SearchFilter(op=Operator.STARTSWITH, field="remarks", value="Jerry")


@pytest.fixture
def nstartswith_filter():
    return SearchFilter(
        op=Operator.NSTARTSWITH, field="remarks", value="Jerry"
    )


@pytest.fixture
def istartswith_filter():
    return SearchFilter(
        op=Operator.ISTARTSWITH, field="remarks", value="jerry"
    )


@pytest.fixture
def nistartswith_filter():
    return SearchFilter(
        op=Operator.NISTARTSWITH, field="remarks", value="jerry"
    )


@pytest.fixture
def endswith_filter():
    return SearchFilter(op=Operator.ENDSWITH, field="remarks", value="Tom")


@pytest.fixture
def nendswith_filter():
    return SearchFilter(op=Operator.NENDSWITH, field="remarks", value="Tom")


@pytest.fixture
def iendswith_filter():
    return SearchFilter(op=Operator.IENDSWITH, field="remarks", value="tom")


@pytest.fixture
def niendswith_filter():
    return SearchFilter(op=Operator.NIENDSWITH, field="remarks", value="tom")


@pytest.fixture
def contains_filter():
    return SearchFilter(op=Operator.CONTAINS, field="remarks", value="Jerry")


@pytest.fixture
def ncontains_filter():
    return SearchFilter(op=Operator.NCONTAINS, field="remarks", value="Jerry")


@pytest.fixture
def icontains_filter():
    return SearchFilter(op=Operator.ICONTAINS, field="remarks", value="jerry")


@pytest.fixture
def nicontains_filter():
    return SearchFilter(op=Operator.NICONTAINS, field="remarks", value="jerry")


@pytest.fixture
def and_filter(gt_filter, lt_filter):
    return And(gt_filter, lt_filter)


@pytest.fixture
def or_filter(gt_filter, lt_filter):
    return Or(gt_filter, lt_filter)


@pytest.fixture
def name_order_asc():
    return OrderBy(field=Pet.name, order=Order.ASC)


@pytest.fixture
def name_order_desc():
    return OrderBy(field="name", order=Order.DESC)


@pytest.fixture
def weight_order_desc():
    return OrderBy(field="weight", order=Order.DESC)


@pytest.fixture
def good_boy_order_desc():
    return OrderBy(field="good_boy", order=Order.DESC)


@pytest.fixture
def weight_neq_none_filter():
    return SearchFilter(op=Operator.NEQ, field="weight", value=None)
