import pytest


def test_initialize(cache_refresh_repository):
    assert cache_refresh_repository is not None
    assert cache_refresh_repository._cache_connector == "test_cache_connector"
    assert cache_refresh_repository._token_model is not None
    assert cache_refresh_repository._token_max_age_seconds is not None
    assert cache_refresh_repository._token_length is not None


def test_get_existing_token(cache_refresh_repository, token):
    with pytest.raises(NotImplementedError):
        cache_refresh_repository.get(token)


def test_get_non_existing_token(cache_refresh_repository):
    non_existing_token = "non_existing_token_value"

    with pytest.raises(NotImplementedError):
        cache_refresh_repository.get(non_existing_token)


def test_create_token(cache_refresh_repository, subject):
    with pytest.raises(NotImplementedError):
        cache_refresh_repository.create(subject)


def test_delete_token(cache_refresh_repository, token):
    with pytest.raises(NotImplementedError):
        cache_refresh_repository.delete(token)


def test_delete_all_tokens(cache_refresh_repository, subject):
    with pytest.raises(NotImplementedError):
        cache_refresh_repository.delete_all(subject)
