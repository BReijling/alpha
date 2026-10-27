import pytest
from alpha import exceptions
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity


def test_static_provider_authenticate(static_provider, static_users):
    identity = static_provider.authenticate(
        PasswordCredentials(
            username=static_users[0]["username"],
            password=static_users[0]["password"],
        )
    )
    assert isinstance(identity, Identity)
    assert identity.subject == static_users[0]["id"]
    assert identity.username == static_users[0]["username"]
    assert identity.display_name == static_users[0]["display_name"]
    assert identity.email == static_users[0]["email"]
    assert identity.groups == static_users[0]["groups"]
    assert identity.permissions == static_users[0]["permissions"]

    with pytest.raises(exceptions.InvalidCredentialsException):
        static_provider.authenticate(
            PasswordCredentials(
                username=static_users[0]["username"],
                password=static_users[1]["password"],
            )
        )


def test_static_provider_get_user(static_provider, static_users):
    identity = static_provider.get_user(static_users[1]["id"])
    assert isinstance(identity, Identity)
    assert identity.subject == static_users[1]["id"]
    assert identity.username == static_users[1]["username"]
    assert identity.display_name == static_users[1]["display_name"]
    assert identity.email == static_users[1]["email"]
    assert identity.groups == static_users[1]["groups"]
    assert identity.permissions == static_users[1]["permissions"]

    with pytest.raises(exceptions.InvalidCredentialsException):
        static_provider.get_user("non_existent_id")


def test_static_provider_change_password(static_provider):
    with pytest.raises(exceptions.NotSupportedException):
        static_provider.change_password("credentials", "new_password")
