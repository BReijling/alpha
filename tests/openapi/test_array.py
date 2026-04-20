import pytest


@pytest.fixture
def path():
    return '/is_array'


@pytest.mark.parametrize(
    'input',
    [
        '1,2,3',
        '1,2',
        '-1,9',
        '321,321',
        '0, 0',
    ],
)
def test_valid_array(path, get, input, parse_response_json):
    response = get(path, input)
    assert response.status_code == 200
    assert parse_response_json(response.data)['data']


@pytest.mark.parametrize(
    'input',
    [
        '1,2,3,4,5',
        'h,h',
        '1,',
        ',1',
        '1.1,1.1',
    ],
)
def test_invalid_array(path, get, input):
    response = get(path, input)
    assert response.status_code == 400
