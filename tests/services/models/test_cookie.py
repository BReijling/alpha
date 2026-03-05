from alpha.services.models.cookie import Cookie


def test_cookie(cookie: Cookie):
    assert cookie.key == "test_cookie"
    assert cookie.value == "test_value"
    assert cookie.operation == "set"
    assert cookie.max_age == 3600
    assert cookie.expires is None
    assert cookie.path == "/"
    assert cookie.domain is None
    assert cookie.secure is False
    assert cookie.httponly is False
    assert cookie.samesite is None
