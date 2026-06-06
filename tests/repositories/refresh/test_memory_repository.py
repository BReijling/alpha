import pytest

from alpha import exceptions
from alpha.providers.models.token import Token


def test_initialize(memory_refresh_repository):
    assert memory_refresh_repository is not None
    assert memory_refresh_repository._refresh_tokens is not None
    assert memory_refresh_repository._token_model is not None
    assert memory_refresh_repository._token_max_age_seconds is not None
    assert memory_refresh_repository._token_length is not None


def test_get_existing_token(memory_refresh_repository, token):
    result = memory_refresh_repository.get(token)
    assert result.value == token


def test_get_non_existing_token(memory_refresh_repository):
    non_existing_token = "non_existing_token_value"

    with pytest.raises(exceptions.NotFoundException):
        memory_refresh_repository.get(non_existing_token)


def test_create_token(memory_refresh_repository, subject):
    token = memory_refresh_repository.create(subject)

    assert token is not None
    assert isinstance(token, Token)
    assert token.subject == subject


def test_delete_token(memory_refresh_repository, token):
    assert memory_refresh_repository.get(token)
    memory_refresh_repository.delete(token)

    with pytest.raises(exceptions.NotFoundException):
        memory_refresh_repository.get(token)


def test_delete_all_tokens(
    memory_refresh_repository, subject, refresh_token_storage_file_path
):
    memory_refresh_repository.create(subject)

    assert len(memory_refresh_repository._refresh_tokens) == 2

    memory_refresh_repository.delete_all(subject)

    assert len(memory_refresh_repository._refresh_tokens) == 0
