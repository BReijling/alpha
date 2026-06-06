import json

import pytest

from alpha import exceptions
from alpha.providers.models.token import Token


def test_initialize(file_refresh_repository):
    assert file_refresh_repository is not None
    assert file_refresh_repository._file_path is not None
    assert file_refresh_repository._token_model is not None
    assert file_refresh_repository._token_max_age_seconds is not None
    assert file_refresh_repository._token_length is not None


def test_get_existing_token(file_refresh_repository, token):
    result = file_refresh_repository.get(token)
    assert result.value == token


def test_get_non_existing_token(file_refresh_repository):
    non_existing_token = "non_existing_token_value"

    with pytest.raises(exceptions.NotFoundException):
        file_refresh_repository.get(non_existing_token)


def test_create_token(file_refresh_repository, subject):
    token = file_refresh_repository.create(subject)

    assert token is not None
    assert isinstance(token, Token)
    assert token.subject == subject


def test_delete_token(file_refresh_repository, token):
    assert file_refresh_repository.get(token)
    file_refresh_repository.delete(token)

    with pytest.raises(exceptions.NotFoundException):
        file_refresh_repository.get(token)


def test_delete_all_tokens(
    file_refresh_repository, subject, refresh_token_storage_file_path
):
    file_refresh_repository.create(subject)

    with open(refresh_token_storage_file_path, "r") as f:
        tokens_data = json.load(f)
        assert len(tokens_data) == 2

    file_refresh_repository.delete_all(subject)

    with open(refresh_token_storage_file_path, "r") as f:
        tokens_data = json.load(f)
        assert len(tokens_data) == 0
