import pytest
from dateutil.parser._parser import ParserError


@pytest.fixture
def path():
    return '/is_date'


@pytest.mark.parametrize(
    'input',
    [
        '2000-01-01',
        '01-01-2021',
        '2000-1-1',
        '2000-01-1',
        '2000-12-31',
        '2222-12-31',
        '2000-2-29',
        '2004-2-29',
        '9999-9-9',
        '1-1-0',
        '2001 01 01',
        '2001 1 1',
        '01-01-1999',
        '01-01-99',
    ],
)
def test_valid_date(path, get, input, parse_response_json):
    response = get(path, input)
    assert response.status_code == 200
    assert parse_response_json(response.data)['data']


@pytest.mark.parametrize(
    'input',
    ['01/01/1999'],
)
def test_invalid_date(path, get, input):
    response = get(path, input)
    assert response.status_code == 404


@pytest.mark.parametrize(
    'input', ['01-2021-01', '2000-31-12', '2002-2-29', '01+01+1999']
)
def test_parser_error(path, get, input):
    with pytest.raises(ParserError):
        get(path, input)
