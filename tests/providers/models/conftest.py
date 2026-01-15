from typing import Any
import pytest

from alpha.providers.models.credentials import PasswordCredentials
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
def token() -> Token:
    return Token("abcdef123456")
