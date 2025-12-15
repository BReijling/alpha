from alpha.utils.response_object import create_response_object


def test_create_response_object():
    obj = create_response_object(status_code=400, status_message="test")

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
    )

    assert obj[1] == 200
    assert obj[0].get("title") == "OK"
    assert obj[0].get("type") == "application/text"
    assert obj[0].get("data") == "data"
