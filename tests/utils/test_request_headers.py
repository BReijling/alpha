import pytest

from alpha.utils.request_headers import Headers


@pytest.mark.parametrize(
    "headers, expected",
    [
        (
            {
                "Authorization": "Bearer abc123",
                "X-Refresh-Token": "refresh123",
                "X-API-Key": "apikey123",
            },
            Headers(
                auth_token="abc123",
                auth_token_type="Bearer",
                refresh_token="refresh123",
                api_key="apikey123",
            ),
        ),
        (
            {
                "Cookie": "auth_token=cookie_auth123; refresh_token=cookie_refresh123; api_key=cookie_apikey123;",
            },
            Headers(
                auth_token="cookie_auth123",
                auth_token_type="Bearer",
                refresh_token="cookie_refresh123",
                api_key="cookie_apikey123",
            ),
        ),
        (
            {
                "Authorization": "Bearer abc123",
                "Cookie": "refresh_token=cookie_refresh123",
            },
            Headers(
                auth_token="abc123",
                auth_token_type="Bearer",
                refresh_token="cookie_refresh123",
                api_key=None,
            ),
        ),
        (
            {
                "X-Refresh-Token": "refresh123",
                "Cookie": "auth_token=cookie_auth123",
            },
            Headers(
                auth_token="cookie_auth123",
                auth_token_type="Bearer",
                refresh_token="refresh123",
                api_key=None,
            ),
        ),
        (
            {
                "Authorization": "Bearer token extra_part",
                "Cookie": "auth_token=cookie_auth123; refresh_token=cookie_refresh123;",
            },
            Headers(
                auth_token="cookie_auth123",
                auth_token_type="Bearer",
                refresh_token="cookie_refresh123",
                api_key=None,
            ),
        ),
        (
            {},
            Headers(
                auth_token=None,
                auth_token_type=None,
                refresh_token=None,
                api_key=None,
            ),
        ),
    ],
)
def test_headers_from_headers(headers, expected):
    result = Headers.from_headers(headers)
    assert result == expected


def test_has_auth_token():
    headers = Headers(auth_token="abc.def.ghi", auth_token_type="Bearer")
    assert headers.has_auth_token is True

    headers = Headers(auth_token="abc.def", auth_token_type="Bearer")
    assert headers.has_auth_token is True

    headers = Headers(auth_token="abc.def.ghi", auth_token_type="Basic")
    assert headers.has_auth_token is False

    headers = Headers(auth_token="abc.def.ghi", auth_token_type=None)
    assert headers.has_auth_token is False

    headers = Headers()
    assert headers.has_auth_token is False

    headers = Headers.from_headers({"Authorization": "Bearer abc.def.ghi"})
    assert headers.has_auth_token is True
    assert headers.auth_token_type == "Bearer"
    assert headers.auth_token == "abc.def.ghi"

    headers = Headers.from_headers({"Cookie": "auth_token=abc.def.ghi;"})
    assert headers.has_auth_token is True
    assert headers.auth_token_type == "Bearer"
    assert headers.auth_token == "abc.def.ghi"


def test_has_refresh_token():
    headers = Headers(refresh_token="refresh123")
    assert headers.has_refresh_token is True

    headers = Headers()
    assert headers.has_refresh_token is False

    headers = Headers.from_headers({"X-Refresh-Token": "refresh123"})
    assert headers.has_refresh_token is True
    assert headers.refresh_token == "refresh123"


def test_has_api_key():
    headers = Headers(api_key="apikey123")
    assert headers.has_api_key is True
    assert headers.api_key == "apikey123"

    headers = Headers()
    assert headers.has_api_key is False

    headers = Headers.from_headers({"X-API-Key": "apikey123"})
    assert headers.has_api_key is True
    assert headers.api_key == "apikey123"


def test_headers_representation(headers: Headers):
    representation = repr(headers)

    assert "Headers(" in representation
    assert "auth_token=***" in representation
    assert "auth_token_type=Bearer" in representation
    assert "refresh_token=***" in representation
    assert "api_key=***" in representation
    assert "cookie_auth123" not in representation
    assert "cookie_refresh123" not in representation
    assert "cookie_apikey123" not in representation
