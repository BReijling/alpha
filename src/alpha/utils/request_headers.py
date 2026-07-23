from dataclasses import dataclass
from http.cookies import SimpleCookie
from typing import Mapping, Self


@dataclass(frozen=True, slots=True)
class Headers:
    """A dataclass representing the headers of an HTTP request. This is
    primarily used for extracting authentication tokens and API keys from the
    request headers and cookies.

    This class provides a convenient way to access authentication tokens and
    API keys, regardless of whether they are provided in the standard headers
    or in cookies. It provides properties to check the presence of these tokens
    and keys.

    This class is designed to be immutable and uses slots for memory
    efficiency.

    Attributes
    ----------
    auth_token
        The authentication token, typically a JWT, extracted from the
        "Authorization" header or from cookies.
    auth_token_type
        The type of the authentication token, typically "Bearer".
    refresh_token
        The refresh token, extracted from the "X-Refresh-Token" header or from
        cookies.
    api_key
        The API key, extracted from the "X-API-Key" header or from cookies.
    cookies
        A mapping of cookie names to their values, if any cookies are present.
    """

    auth_token: str | None = None
    auth_token_type: str | None = None
    refresh_token: str | None = None
    api_key: str | None = None
    _cookie_jar: SimpleCookie | None = None

    @classmethod
    def from_headers(
        cls,
        headers: Mapping[str, str],
        auth_token_cookie_name: str = "auth_token",
        refresh_token_cookie_name: str = "refresh_token",
        api_key_cookie_name: str = "api_key",
    ) -> Self:
        """Create a Headers instance from a mapping of headers.

        For the auth token, the method first checks the "Authorization" header.
        If present, it extracts the token and its type (e.g., "Bearer"). If it
        is not present, it looks for a cookie with the name specified by
        `auth_token_cookie_name`. The same logic applies to the refresh token
        and API key, checking the "X-Refresh-Token" and "X-API-Key" headers. If
        they are not present, it looks for cookies with the names specified by
        `refresh_token_cookie_name` and `api_key_cookie_name`.

        Parameters
        ----------
        headers
            A mapping of header names to their values.
        auth_token_cookie_name
            The name of the cookie containing the auth token, default is
            "auth_token".
        refresh_token_cookie_name
            The name of the cookie containing the refresh token, default is
            "refresh_token".
        api_key_cookie_name
            The name of the cookie containing the API key, default is
            "api_key".

        Returns
        -------
            An instance of the Headers class.
        """
        auth_token = None
        auth_token_type = None
        authorization_header = headers.get("Authorization")
        if authorization_header is not None:
            parts = authorization_header.split()
            if len(parts) == 2:
                auth_token_type, auth_token = parts
                if auth_token_type.lower() == "bearer":
                    auth_token_type = "Bearer"

        refresh_token = headers.get("X-Refresh-Token")
        api_key = headers.get("X-API-Key")
        cookies_header = headers.get("Cookie")

        cookie_jar: SimpleCookie | None = None
        if cookies_header is not None:
            cookie_jar = SimpleCookie(cookies_header)

            if not auth_token and auth_token_cookie_name in cookie_jar:
                auth_token = cookie_jar[auth_token_cookie_name].value
                auth_token_type = "Bearer"
            if not refresh_token and refresh_token_cookie_name in cookie_jar:
                refresh_token = cookie_jar[refresh_token_cookie_name].value
            if not api_key and api_key_cookie_name in cookie_jar:
                api_key = cookie_jar[api_key_cookie_name].value

        return cls(
            auth_token=auth_token,
            auth_token_type=auth_token_type,
            refresh_token=refresh_token,
            api_key=api_key,
            _cookie_jar=cookie_jar,
        )

    @property
    def has_auth_token(self) -> bool:
        if not self.auth_token:
            return False
        if not self.auth_token_type:
            return False
        return self.auth_token_type.lower() == "bearer"

    @property
    def has_refresh_token(self) -> bool:
        return True if self.refresh_token else False

    @property
    def has_api_key(self) -> bool:
        return True if self.api_key else False

    @property
    def cookies(self) -> dict[str, str]:
        """Return a dictionary of cookies extracted from the request headers.

        Returns
        -------
        dict[str, str]
            A dictionary mapping cookie names to their values. If no cookies
            are present, an empty dictionary is returned.
        """
        if self._cookie_jar is None:
            return {}
        return self._cookie_jar_to_dict(self._cookie_jar)

    def __repr__(self) -> str:
        return (
            f"Headers(auth_token={'***' if self.auth_token else None}, "
            f"auth_token_type={self.auth_token_type}, "
            f"refresh_token={'***' if self.refresh_token else None}, "
            f"api_key={'***' if self.api_key else None})"
        )

    @staticmethod
    def _cookie_jar_to_dict(cookie_jar: SimpleCookie) -> dict[str, str]:
        """Convert a SimpleCookie object to a dictionary.

        Parameters
        ----------
        cookie_jar
            A SimpleCookie object containing the cookies.

        Returns
        -------
        dict[str, str]
            A dictionary mapping cookie names to their values.
        """
        return {key: morsel.value for key, morsel in cookie_jar.items()}
