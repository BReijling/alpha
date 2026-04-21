import pytest

from alpha.services.models.cookie import Cookie
from alpha.utils.request_headers import Headers


@pytest.fixture
def example_set_cookie1():
    return Cookie(
        key="test_cookie1", value="test_value", max_age=3600, path="/"
    )


@pytest.fixture
def example_set_cookie2():
    return Cookie(
        key="test_cookie2", value="test_value", max_age=3600, path="/"
    )


@pytest.fixture
def example_delete_cookie():
    return Cookie(
        key="test_cookie1",
        operation="delete",
        path="/",
    )


@pytest.fixture
def headers() -> Headers:
    return Headers(
        auth_token="cookie_auth123",
        auth_token_type="Bearer",
        refresh_token="cookie_refresh123",
        api_key="cookie_apikey123",
    )
