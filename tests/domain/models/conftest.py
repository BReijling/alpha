import pytest

from alpha.domain.models.permission import Permission
from alpha.domain.models.user import User
from alpha.domain.models.group import Group


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
