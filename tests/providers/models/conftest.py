from typing import Any
import pytest

from alpha.domain.models.group import Group
from alpha.domain.models.permission import Permission
from alpha.domain.models.user import User
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token


@pytest.fixture
def ldap_dict() -> dict[str, Any]:
    return {
        "uid": ["ldap_user"],
        # "cn": "LDAP User",
        "mail": ["ldap_user@example.com"],
        "memberOf": [
            "cn=group1,dc=example,dc=com",
            "cn=group2,dc=example,dc=com",
        ],
    }


@pytest.fixture
def ad_dict() -> dict[str, Any]:
    return {
        "sAMAccountName": ["ad_user"],
        "cn": ["AD User"],
        "displayName": ["Display AD User"],
        "mail": ["ad_user@example.com"],
        "memberOf": [
            "CN=group1,DC=example,DC=com",
            "CN=group2,DC=example,DC=com",
            "CN=group3\\, with\\, commas,DC=example,DC=com",
        ],
    }


@pytest.fixture
def password_credentials() -> PasswordCredentials:
    return PasswordCredentials(
        username="testuser", password="securepassword123"
    )


@pytest.fixture
def identity_admin1() -> Identity:
    return Identity.from_dict(
        {
            "subject": "admin_user1",
            "admin": True,
        }
    )


@pytest.fixture
def identity_admin2() -> Identity:
    return Identity.from_dict(
        {
            "subject": "admin_user2",
            "role": "ADMIN",
        }
    )


@pytest.fixture
def identity_admin3() -> Identity:
    return Identity.from_dict(
        {
            "subject": "admin_user3",
            "permissions": ["ADMIN"],
        }
    )


@pytest.fixture
def identity_no_admin() -> Identity:
    return Identity.from_dict(
        {
            "subject": "no_admin_user",
            "permissions": ["read", "write"],
        }
    )


@pytest.fixture
def token() -> Token:
    return Token("abcdef123456")


@pytest.fixture
def user() -> User:
    return User(
        id=1,
        username="testuser",
        email="testuser@example.com",
        display_name="Test User",
        groups=[],
        permissions=[],
        role="USER",
        admin=False,
    )


@pytest.fixture
def user_with_string_groups(user: User) -> User:
    user.groups = ["group1", "group2"]
    return user


@pytest.fixture
def user_with_model_groups(user: User) -> User:
    user.groups = [Group(name="group1"), Group(name="group2")]
    return user


@pytest.fixture
def user_with_string_permissions(user: User) -> User:
    user.permissions = ["permission1", "permission2"]
    return user


@pytest.fixture
def user_with_model_permissions(user: User) -> User:
    user.permissions = [
        Permission(name="permission1"),
        Permission(name="permission2"),
    ]
    return user
