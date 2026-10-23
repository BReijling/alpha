from dataclasses import dataclass, field
import pytest

from alpha.domain.models.permission import Permission
from alpha.domain.models.user import User
from alpha.domain.models.group import Group


@dataclass
class NewUser(User):
    """User dataclass to patch the User class of the alpha library."""

    permissions: list[Permission] = field(default_factory=list)  # type: ignore
    groups: list[Group] = field(default_factory=list)  # type: ignore


@dataclass
class NewGroup(Group):
    """Group dataclass to patch the Group class of the alpha library."""

    permissions: list[Permission] = field(default_factory=list)  # type: ignore


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


@pytest.fixture
def user_with_string_collections():
    return User(username="user", email="user@example.com")


@pytest.fixture
def user_with_object_collections():
    return NewUser(username="newuser", email="newuser@example.com")


@pytest.fixture
def group_with_object_collections():
    return NewGroup(name="newgroup")
