from datetime import datetime, date, tzinfo
from typing import overload, Literal


@overload
def to_datetime(
    value: str | datetime | None,
    tz: tzinfo | None = None,
    fail_silently: Literal[False] = False,
) -> datetime | None: ...


@overload
def to_datetime(
    value: str | datetime | None,
    tz: tzinfo | None = None,
    fail_silently: Literal[True] = True,
) -> str | datetime | None: ...


def to_datetime(
    value: str | datetime | None,
    tz: tzinfo | None = None,
    fail_silently: bool = True,
) -> str | datetime | None:
    """Parse a string to a datetime object if possible.

    Parameters
    ----------
    value
        The string to parse.
    tz
        The timezone information to apply to the parsed datetime object.
        If None, the datetime will be naive.
    fail_silently
        If True, return the original string when parsing fails.
        If False, raise a ValueError when parsing fails.

    Returns
    -------
        The parsed datetime object or the original string if parsing fails.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        if tz is not None:
            return value.astimezone(tz)
        return value
    try:
        dt = datetime.fromisoformat(value)
        if tz is not None:
            dt = dt.astimezone(tz)
        return dt
    except (ValueError, TypeError) as e:
        if fail_silently:
            return value
        raise type(e)(f"Failed to parse datetime from value: {value}") from e


@overload
def to_date(
    value: str | date | None, fail_silently: Literal[False] = False
) -> date | None: ...


@overload
def to_date(
    value: str | date | None, fail_silently: Literal[True] = True
) -> str | date | None: ...


def to_date(
    value: str | date | None, fail_silently: bool = True
) -> str | date | None:
    """Parse a string to a date object if possible.

    Parameters
    ----------
    value
        The string to parse. Can also be None.
    fail_silently
        If True, return the original string when parsing fails.
        If False, raise a ValueError when parsing fails.

    Returns
    -------
        The parsed date object or the original string if parsing fails.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError) as e:
        if fail_silently:
            return value
        raise type(e)(f"Failed to parse date from value: {value}") from e
