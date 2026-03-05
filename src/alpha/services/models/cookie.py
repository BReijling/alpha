from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal


@dataclass(frozen=True)
class Cookie:
    """Represents an HTTP cookie.

    Parameters
    ----------
    key
        The name of the cookie.
    value
        The value of the cookie.
    operation
        The operation to perform on the cookie, either "set" or "delete".
        Defaults to "set".
    max_age
        The maximum age of the cookie in seconds. If None, the cookie will last
        only as long as the client’s browser session. Defaults to None.
    expires
        The expiration date of the cookie. Can be a datetime object, a UNIX
        timestamp, or None. Defaults to None.
    path
        The path for which the cookie is valid. If None, the cookie will be
        valid for the entire domain. Defaults to "/".
    domain
        The domain for which the cookie is valid. If None, the cookie will only
        be valid for the domain that set it. Defaults to None.
    secure
        If True, the cookie will only be available via HTTPS. Defaults to
        False.
    httponly
        If True, JavaScript will not be able to access the cookie. Defaults to
        False.
    samesite
        The SameSite attribute of the cookie, which can be "Strict", "Lax", or
        "None". Defaults to None.
    """

    key: str
    value: str = ""
    operation: Literal["set", "delete"] = "set"
    max_age: timedelta | int | None = None
    expires: str | datetime | int | float | None = None
    path: str = "/"
    domain: str | None = None
    secure: bool = False
    httponly: bool = False
    samesite: str | None = None
