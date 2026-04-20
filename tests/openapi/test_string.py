import pytest


@pytest.fixture
def path():
    return '/verify_string'


@pytest.mark.parametrize(
    'input',
    [
        'ALPHA',
        'BRAVO',
        'DELTA',
        'GAMMA',
    ],
)
def test_valid_strings(path, get, input, parse_response_json):
    response = get(path, input)
    assert response.status_code == 204


@pytest.mark.parametrize(
    'input',
    [
        'ALPH',
        'ALPHAS',
        'ALPH1',
        'aLPHA',
        'ALPHA ',
        ' ALPHA',
        '12345',
    ],
)
def test_invalid_strings(path, get, input, parse_response_json):
    response = get(path, input)
    assert response.status_code == 400
