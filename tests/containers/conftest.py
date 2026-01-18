import pytest

from alpha.containers.container import Container


@pytest.fixture
def container():
    return Container()
