import json

import pytest
from flask.wrappers import Response

from alpha.utils.response_object import create_response_object


def test_create_response_object():
    obj = create_response_object(
        status_code=400,
        status_message="test",
        data="test",
        response_format=None,
    )

    assert isinstance(obj, tuple)

    response_obj, status_code = obj
    assert isinstance(response_obj, dict)
    assert status_code == 400

    assert response_obj["detail"] == "test"
    assert response_obj["status"] == 400
    assert response_obj["title"] == "Bad Request"
    assert response_obj["type"] == "application/json"
    assert response_obj["data"] == "test"

    with pytest.raises(ValueError):
        create_response_object(
            status_code=200,
            status_message="test",
            response_format="invalid_type",
        )


def test_create_response_object_accept_header_all():
    obj = create_response_object(
        status_code=200,
        status_message="test",
        data="string_data",
        accept_header="*/*",
        supported_data_types=["application/xml", "application/json"],
        response_format=None,
    )

    response_obj, status_code = obj
    assert isinstance(response_obj, dict)
    assert status_code == 200

    assert response_obj["type"] == "application/xml"
    assert response_obj["data"] == "string_data"


def test_create_response_object_accept_header_all_subtypes():
    obj = create_response_object(
        status_code=200,
        status_message="test",
        data="string_data",
        accept_header="/*",
        supported_data_types=["application/json", "application/xml"],
        response_format=None,
    )

    response_obj, status_code = obj
    assert isinstance(response_obj, dict)
    assert status_code == 200

    assert response_obj["type"] == "application/json"
    assert response_obj["data"] == "string_data"


def test_create_response_object_accept_header_default():
    obj = create_response_object(
        status_code=200,
        status_message="test",
        data="string_data",
        accept_header="/",
        supported_data_types=["application/xml"],
        response_format=None,
    )

    response_obj, status_code = obj
    assert isinstance(response_obj, dict)
    assert status_code == 200

    assert response_obj["type"] == "application/json"
    assert response_obj["data"] == "string_data"


def test_create_response_object_with_flask_response():
    obj = create_response_object(
        status_code=200,
        status_message="test",
        data="string_data",
        accept_header="application/text",
        supported_data_types=["application/text"],
        response_format="flask",
    )

    response_obj, status_code = obj
    assert isinstance(response_obj, Response)
    assert isinstance(response_obj.data, bytes)
    assert response_obj.mimetype == "application/text"
    assert status_code == 200

    response_data = response_obj.data.decode("utf-8")
    assert isinstance(response_data, str)

    response_dict = json.loads(response_data)
    assert isinstance(response_dict, dict)
    assert response_dict["data"] == "string_data"


def test_create_response_object_with_cookie(
    example_set_cookie1,
):
    obj = create_response_object(
        status_code=200,
        status_message="test",
        data=example_set_cookie1,
        response_format="flask",
    )

    response_obj, _ = obj

    headers = response_obj.headers
    assert headers.get("Set-Cookie") is not None

    cookie_headers = headers.get_all("Set-Cookie")
    assert len(cookie_headers) == 1
    assert "test_cookie1" in cookie_headers[0]

    response_data = response_obj.data.decode("utf-8")
    assert isinstance(response_data, str)

    response = json.loads(response_data)
    assert isinstance(response, dict)
    assert "data" not in response


def test_create_response_object_with_cookies(
    example_set_cookie1, example_set_cookie2, example_delete_cookie
):
    obj = create_response_object(
        status_code=200,
        status_message="test",
        data=(example_set_cookie1, example_set_cookie2, example_delete_cookie),
        response_format="flask",
    )

    response_obj, _ = obj

    headers = response_obj.headers
    assert headers.get("Set-Cookie") is not None

    cookie_headers = headers.get_all("Set-Cookie")
    assert len(cookie_headers) == 3
    assert "test_cookie1" in cookie_headers[0]
    assert "test_cookie2" in cookie_headers[1]
    assert "test_cookie1" in cookie_headers[2]


def test_create_response_object_with_mixed_data_string(example_set_cookie1):
    obj = create_response_object(
        status_code=200,
        status_message="test",
        data=(example_set_cookie1, "string_data"),
        response_format="flask",
    )

    response_obj, _ = obj

    headers = response_obj.headers
    assert headers.get("Set-Cookie") is not None

    cookie_headers = headers.get_all("Set-Cookie")
    assert len(cookie_headers) == 1
    assert "test_cookie1" in cookie_headers[0]

    response_data = response_obj.data.decode("utf-8")
    assert isinstance(response_data, str)

    response = json.loads(response_data)
    assert isinstance(response, dict)
    assert response["data"] == "string_data"


def test_create_response_object_with_mixed_data_list(example_set_cookie1):
    obj = create_response_object(
        status_code=200,
        status_message="test",
        data=(example_set_cookie1, ["string_data"]),
        response_format="flask",
    )

    response_obj, _ = obj

    response_data = response_obj.data.decode("utf-8")
    assert isinstance(response_data, str)

    response = json.loads(response_data)
    assert isinstance(response, dict)
    assert response["data"] == ["string_data"]


def test_create_response_object_with_mixed_data_empty_list(
    example_set_cookie1,
):
    obj = create_response_object(
        status_code=200,
        status_message="test",
        data=(example_set_cookie1, []),
        response_format="flask",
    )

    response_obj, _ = obj

    response_data = response_obj.data.decode("utf-8")
    assert isinstance(response_data, str)

    response = json.loads(response_data)
    assert isinstance(response, dict)
    assert response["data"] == []
