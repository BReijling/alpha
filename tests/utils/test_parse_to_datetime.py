from datetime import datetime, date
import pytest
from alpha.utils.parse_to_datetime import to_datetime, to_date


def test_parse_to_datetime(datetime_iso):
    result = to_datetime(datetime_iso)
    assert isinstance(result, datetime)

    result = to_datetime(result)
    assert isinstance(result, datetime)
    assert result.isoformat() == datetime_iso

    test_string = "test_string"
    result = to_datetime(test_string)
    assert result == test_string

    result = to_datetime(None)
    assert result is None

    integer = 123
    result = to_datetime(integer)
    assert result == integer

    with pytest.raises(ValueError):
        to_datetime(test_string, fail_silently=False)
    with pytest.raises(TypeError):
        to_datetime(123, fail_silently=False)


def test_parse_to_date(date_iso):
    result = to_date(date_iso)
    assert isinstance(result, date)

    result = to_date(result)
    assert isinstance(result, date)
    assert result.isoformat() == date_iso

    test_string = "test_string"
    result = to_date(test_string)
    assert result == test_string

    result = to_date(None)
    assert result is None

    integer = 123
    result = to_date(integer)
    assert result == integer

    with pytest.raises(ValueError):
        to_date(test_string, fail_silently=False)
    with pytest.raises(TypeError):
        to_date(integer, fail_silently=False)
