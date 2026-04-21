import pytest
from dateutil.parser import ParserError


@pytest.fixture
def path():
    return "/is_datetime"


@pytest.mark.parametrize(
    "input",
    [
        "2000-01-01T01:01:01",
        "2000-1-1T01:01:01+02:00",
        "01-01-2021T01:01:01 UTC",
        "01-01-2021T01:01:01 WAT",
        "01-01-2021T01:01:01 EST",
        "01-01-2021T01:01:01 MSK",
        "01-01-2021T01:01:01 HST",
        "01-01-2021T01:01:01Z",
        "2000-1-1T01:01:01+0200",
        "2000-01-1",
        "2000-12-31",
        "2000-2-29",
        "2000-1-1T01:01:01+02",
        "2000-1-1T1:1:1+2",  # not iso-format
        "2000-1-1T01:01:01+2",  # not iso-format
    ],
)
def test_valid_datetime(path, get, input, parse_response_json):
    response = get(path, input)
    assert response.status_code == 200
    assert parse_response_json(response.data)["data"]


@pytest.mark.parametrize(
    "input",
    [
        "01-01-2021T01:01:01 Asia/Shanghai",
        "01-01-2021T01:01:01 Europe/London",
    ],
)
def test_invalid_datetime(path, get, input):
    response = get(path, input)
    assert response.status_code == 404


@pytest.mark.parametrize(
    "input", ["2000-1-1T01:01:01+02:00:00", "2000-1-1T01:01:01+02:00:00.000"]
)
def test_parser_error(path, get, input):
    with pytest.raises(ParserError):
        get(path, input)
