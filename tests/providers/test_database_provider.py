import pytest
from alpha.exceptions import (
    InvalidCredentialsException,
    MissingPasswordException,
    UserNotFoundException,
)
from alpha.factories.password_factory import PasswordFactory
from alpha.providers.models.identity import Identity


def test_database_provider(database_provider):
    assert database_provider.protocol == "database"
    assert database_provider.token_factory is None
    assert isinstance(database_provider._password_factory, PasswordFactory)
    assert database_provider._user_name_attribute == "username"
    assert database_provider._users_repository_name == "database_provider"


def test_database_provider_authenticate(
    database_provider,
    database_provider_empty_password,
    database_provider_no_user,
    credentials,
    wrong_credentials,
):
    result = database_provider.authenticate(credentials)

    assert isinstance(result, Identity)

    assert result.subject == "1"
    assert result.username == "test_user"
    assert result.email == "test_user@example.com"

    # Verify that authenticating with wrong credentials raises the appropriate
    # exception
    with pytest.raises(InvalidCredentialsException):
        database_provider.authenticate(credentials=wrong_credentials)

    # Verify that authenticating a user with an empty password raises the
    # appropriate exception
    with pytest.raises(MissingPasswordException):
        database_provider_empty_password.authenticate(credentials)

    # Verify that requesting a non-existent user raises the appropriate
    # exception
    with pytest.raises(UserNotFoundException):
        database_provider_no_user.authenticate(credentials)


def test_database_provider_get_user(
    database_provider, database_provider_no_user
):
    result = database_provider.get_user("test_user")
    assert isinstance(result, Identity)

    assert result.subject == "1"
    assert result.username == "test_user"
    assert result.email == "test_user@example.com"

    # Verify that requesting a non-existent user raises the appropriate
    # exception
    with pytest.raises(UserNotFoundException):
        database_provider_no_user.get_user("test_user")


def test_database_provider_change_password(
    database_provider, database_provider_no_user, credentials
):
    new_password = "new_secure_password"
    database_provider.change_password(credentials, new_password)

    # Verify that the password was changed successfully
    with pytest.raises(InvalidCredentialsException):
        database_provider.authenticate(credentials)

    # Verify that requesting a non-existent user raises the appropriate
    # exception
    with pytest.raises(UserNotFoundException):
        database_provider_no_user.change_password(credentials, new_password)
