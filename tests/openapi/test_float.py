import pytest


@pytest.fixture
def path():
    return '/is_float'


@pytest.mark.parametrize(
    'input',
    [-1, -1.3, 0, 0.0, 1.8, 30],
)
def test_valid_float(path, get, input, parse_response_json):
    response = get(path, input)
    assert response.status_code == 200
    assert parse_response_json(response.data)['data']


@pytest.mark.parametrize(
    'input',
    [None, 'I', '3-3', '1e3'],
)
def test_invalid_float(path, get, input):
    response = get(path, input)
    assert response.status_code == 404


@pytest.mark.parametrize(
    'input',
    [''],
)
def test_value_error(path, get, input):
    with pytest.raises(ValueError):
        get(path, input)
