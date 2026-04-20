import pytest
from dateutil.parser._parser import ParserError


@pytest.fixture
def path():
    return '/check_datetime_tz_offset'


@pytest.mark.parametrize(
    'input',
    [
        '2000-01-01T01:01:01+02:00',
        '2000-1-1T01:01:01+02:00',
        '2000-1-1T01:01:01+0200',
        '2000-1-1T01:01:01+02',
        '2000-1-1T01:01:01+2',
        '2000-1-1T1:1:1+2',
    ],
)
def test_correct(path, get, parse_response_json, input):
    response = get(path, input)
    assert response.status_code == 200
    assert parse_response_json(response.data)['data']


@pytest.mark.parametrize(
    'input',
    [
        '2000-01-01T01:01:01',
        '2000-01-1',
        '2000-12-31',
        '2000-2-29',
        '01-01-2021T01:01:01Z',
        '01-01-2021T01:01:01 UTC',
        '01-01-2021T01:01:01 WAT',
        '01-01-2021T01:01:01 EST',
        '01-01-2021T01:01:01 MSK',
        '01-01-2021T01:01:01 HST',
    ],
)
def test_incorrect(path, get, parse_response_json, input):
    response = get(path, input)
    assert response.status_code == 200
    assert not parse_response_json(response.data)['data']


@pytest.mark.parametrize(
    'input',
    [
        '01-01-2021T01:01:01 Asia/Shanghai',
        '01-01-2021T01:01:01 Europe/London',
    ],
)
def test_invalid(path, get, input):
    response = get(path, input)
    assert response.status_code == 404


@pytest.mark.parametrize(
    'input',
    [
        '2000-2-291T01:01:01Z+99:00',
        '2000-1-1T111+2',
        '2000-1-1T1430.5+02',
    ],
)
def test_parser_error(path, get, input):
    with pytest.raises(ParserError):
        get(path, input)


@pytest.mark.parametrize(
    'input',
    [
        '2000-1-1T01:01:01+99:00',
    ],
)
def test_value_error(path, get, input):
    with pytest.raises(ValueError):
        get(path, input)
