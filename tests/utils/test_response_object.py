from flask import Response
from alpha.utils.response_object import create_response_object


def test_create_response_object():
    obj = create_response_object(
        status_code=400,
        status_message="test",
        response_type=None,
    )

    assert isinstance(obj, tuple)

    assert obj[1] == 400
    assert obj[0].get("detail") == "test"
    assert obj[0].get("status") == 400
    assert obj[0].get("title") == "Bad Request"
    assert obj[0].get("type") == "application/json"

    obj = create_response_object(
        status_code=200,
        status_message="test",
        data="data",
        data_type="application/text",
        response_type="flask",
    )

    assert isinstance(obj[0], Response)

    assert obj[1] == 200
    assert obj[0].response.get("title") == "OK"
    assert obj[0].response.get("type") == "application/text"
    assert obj[0].response.get("data") == "data"


def test_create_response_object_with_cookies(
    example_set_cookie1, example_set_cookie2, example_delete_cookie
):
    obj = create_response_object(
        status_code=200,
        status_message="test",
        data=(example_set_cookie1, example_set_cookie2, example_delete_cookie),
        response_type="flask",
    )

    headers = obj[0].headers
    assert headers.get("Set-Cookie") is not None

    cookie_headers = headers.get_all("Set-Cookie")
    assert "test_cookie1" in cookie_headers[0]
    assert "test_cookie2" in cookie_headers[1]
    assert "test_cookie1" in cookie_headers[2]
