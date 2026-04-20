import pytest


@pytest.fixture
def path():
    return '/is_integer'


@pytest.mark.parametrize(
    'input',
    [-1, 0, 1, 2, 30],
)
def test_valid_integer(path, get, input, parse_response_json):
    response = get(path, input)
    assert response.status_code == 200
    assert parse_response_json(response.data)['data']


@pytest.mark.parametrize(
    'input',
    [-1.3, 0.0, 1.8, 30.3, '', 'I', None, '1e3'],
)
def test_invalid_integer(path, get, input):
    response = get(path, input)
    assert response.status_code == 404
