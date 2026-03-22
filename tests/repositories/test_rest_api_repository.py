from tests.fixtures._domain_models import TestModel


def test_rest_api_repository(rest_api_repository):
    assert rest_api_repository is not None
    assert rest_api_repository._session is not None
    assert rest_api_repository._host.startswith("http://127.0.0.1:")
    assert rest_api_repository._base_path == ""
    assert rest_api_repository._endpoint == "/objects"
    assert rest_api_repository._default_model == TestModel
    assert rest_api_repository._model_factory_method_name == "factory"
    assert rest_api_repository._response_data_attribute == "data"


def test_rest_api_repository_get(rest_api_repository):
    response = rest_api_repository.get(param=1)

    assert isinstance(response, TestModel)
    assert response.value == "1"

    response = rest_api_repository.get(param=1, use_factory=False)

    assert isinstance(response, dict)
    assert response["value"] == "1"

    response = rest_api_repository.get(
        parent_endpoint="parents", parent_param=123, param=321
    )
    assert isinstance(response, TestModel)
    assert response.value == "123_321"


def test_rest_api_repository_get_all(rest_api_repository):
    response = rest_api_repository.get_all()

    assert isinstance(response, list)
    assert all(isinstance(item, TestModel) for item in response)
    assert response[0].value == "abc"
    assert response[1].value == "def"

    response = rest_api_repository.get_all(use_factory=False)

    assert isinstance(response, list)
    assert all(isinstance(item, dict) for item in response)
    assert response[0]["value"] == "abc"
    assert response[1]["value"] == "def"


def test_rest_api_repository_add(rest_api_repository, test_model):
    response = rest_api_repository.add(
        endpoint=f"{rest_api_repository._host}/objects",
        obj=test_model,
    )

    assert isinstance(response, TestModel)
    assert response.value == test_model.value

    response = rest_api_repository.add(
        endpoint=f"{rest_api_repository._host}/objects",
        obj=test_model,
        use_factory=False,
    )

    assert isinstance(response, dict)
    assert response["value"] == test_model.value

    response = rest_api_repository.add(
        endpoint=f"{rest_api_repository._host}/objects",
        obj=test_model,
        return_obj=False,
    )

    assert response is None


def test_rest_api_repository_add_no_serialization(
    rest_api_repository_no_serialization, test_model
):
    response = rest_api_repository_no_serialization.add(
        endpoint=f"{rest_api_repository_no_serialization._host}/objects",
        obj={"value": test_model.value},
        serialize=False,
    )

    assert isinstance(response, TestModel)
    assert response.value == test_model.value


def test_rest_api_repository_add_all(rest_api_repository, test_model):
    response = rest_api_repository.add_all(
        endpoint=f"{rest_api_repository._host}/objects",
        objs=[test_model, test_model],
    )

    assert isinstance(response, list)
    assert all(isinstance(item, TestModel) for item in response)
    assert all(item.value == test_model.value for item in response)

    response = rest_api_repository.add_all(
        endpoint=f"{rest_api_repository._host}/objects",
        objs=[test_model, test_model],
        use_factory=False,
    )

    assert isinstance(response, list)
    assert all(isinstance(item, dict) for item in response)
    assert all(item["value"] == test_model.value for item in response)

    response = rest_api_repository.add_all(
        endpoint=f"{rest_api_repository._host}/objects",
        objs=[test_model, test_model],
        return_objs=False,
    )

    assert response is None


def test_rest_api_repository_add_all_one_by_one(
    rest_api_repository, test_model
):
    response = rest_api_repository.add_all(
        endpoint=f"{rest_api_repository._host}/objects",
        objs=[test_model, test_model],
        one_by_one=True,
    )

    assert isinstance(response, list)
    assert all(isinstance(item, TestModel) for item in response)
    assert all(item.value == test_model.value for item in response)


def test_rest_api_repository_remove(rest_api_repository, test_model):
    response = rest_api_repository.remove(
        endpoint=f"{rest_api_repository._host}/objects",
        param="abc",
    )

    assert response is None


def test_rest_api_repository_update(rest_api_repository, test_model):
    response = rest_api_repository.update(
        endpoint=f"{rest_api_repository._host}/objects",
        obj=test_model,
    )

    assert isinstance(response, TestModel)
    assert response.value == test_model.value

    response = rest_api_repository.update(
        endpoint=f"{rest_api_repository._host}/objects",
        obj=test_model,
        use_factory=False,
    )

    assert isinstance(response, dict)
    assert response["value"] == test_model.value

    response = rest_api_repository.update(
        endpoint=f"{rest_api_repository._host}/objects",
        obj=test_model,
        return_obj=False,
    )

    assert response is None


def test_rest_api_repository__build_url(
    rest_api_repository, rest_api_repository_for_build_url
):
    url = rest_api_repository._build_url(endpoint="objects")
    assert url == f"{rest_api_repository._host}/objects"

    url_with_base = rest_api_repository_for_build_url._build_url()
    assert url_with_base == "http://localhost:5000/api/v1/objects"

    url_with_base_and_endpoint = rest_api_repository_for_build_url._build_url(
        endpoint="another-endpoint"
    )
    assert (
        url_with_base_and_endpoint
        == "http://localhost:5000/api/v1/another-endpoint"
    )

    url_with_base_endpoint_and_param = (
        rest_api_repository_for_build_url._build_url(
            endpoint="parents/1/children", param=123
        )
    )
    assert (
        url_with_base_endpoint_and_param
        == "http://localhost:5000/api/v1/parents/1/children/123"
    )

    url_with_base_parent_param_and_params = (
        rest_api_repository_for_build_url._build_url(
            parent_endpoint="parents",
            parent_param=321,
            param=123,
            limit=10,
            offset=20,
        )
    )
    assert (
        url_with_base_parent_param_and_params
        == "http://localhost:5000/api/v1/parents/321/objects/123?limit=10&offset=20"
    )
