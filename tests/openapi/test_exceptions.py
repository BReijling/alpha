import pytest


@pytest.fixture
def exceptions_path():
    return '/exceptions'


def test_bad_request_exception(post, invalid_pet_dict, exceptions_path):
    response = post(exceptions_path, invalid_pet_dict)
    assert response.status_code == 400


def test_access_forbidden_exception(post, cat_dict, exceptions_path):
    response = post(exceptions_path, cat_dict)
    assert response.status_code == 403


def test_unprocessable_content_exception(post, bad_pet_dict, exceptions_path):
    response = post(exceptions_path, bad_pet_dict)
    assert response.status_code == 422


@pytest.mark.parametrize(
    'input',
    [
        400,
        401,
        403,
        404,
        405,
        406,
        409,
        413,
        422,
    ],
)
def test_client_error_exceptions(get, input):
    response = get(f'/raise/{input}')
    assert response.status_code == int(input)


@pytest.mark.parametrize(
    'input',
    [
        500,
        501,
        502,
        503,
        504,
    ],
)
def test_server_error_exceptions(get, input):
    response = get(f'/raise/{input}')
    assert response.status_code == int(input)
