def test_root_endpoint(get, parse_response_json):
    response = get("/")
    assert response.status_code == 200
    data = parse_response_json(response.data)
    assert data["status_code"] == 200
    assert data["data"] == "API is running"


def test_raw_response(get):
    response = get("/raw_response")
    assert response.status_code == 200

    assert response.data == b"123"


def test_response_model(post, pet_dict):
    response = post("/dataclass/factory_response", pet_dict)

    assert response.status_code == 201

    # Check readOnly attributes
    assert response.json["data"]["id"] == 1
    assert response.json["data"]["name"] == "Pluto"
    assert "age" not in response.json.keys()

    # Check response object keys
    assert "detail" in response.json.keys()
    assert "status" in response.json.keys()
    assert "type" in response.json.keys()
    assert "title" in response.json.keys()
