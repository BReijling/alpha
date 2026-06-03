import pytest

from alpha import exceptions
from alpha.providers.models.token import Token


def test_initialize(database_refresh_repository):
    assert database_refresh_repository is not None
    assert database_refresh_repository._database_connector is not None
    assert database_refresh_repository._token_model is not None
    assert database_refresh_repository._token_max_age_seconds is not None
    assert database_refresh_repository._token_length is not None


def test_get_existing_token(database_refresh_repository, token):
    result = database_refresh_repository.get(token)
    assert result == token


def test_get_non_existing_token(database_refresh_repository_no_token):
    non_existing_token = "non_existing_token_value"

    with pytest.raises(exceptions.NotFoundException):
        database_refresh_repository_no_token.get(non_existing_token)


def test_create_token(database_refresh_repository, subject):
    token = database_refresh_repository.create(subject)

    assert token is not None
    assert isinstance(token, Token)
    assert token.subject == subject


def test_delete_token(database_refresh_repository, token):
    assert database_refresh_repository.get(token)
    database_refresh_repository.delete(token)

    with pytest.raises(exceptions.NotFoundException):
        database_refresh_repository.get(token)


def test_delete_all_tokens(database_refresh_repository, subject):
    database_refresh_repository.create(subject)

    assert (
        len(database_refresh_repository._database_connector.get_session().objs)
        == 2
    )

    database_refresh_repository.delete_all(subject)

    assert (
        len(database_refresh_repository._database_connector.get_session().objs)
        == 0
    )
