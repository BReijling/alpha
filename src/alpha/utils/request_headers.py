from dataclasses import dataclass
from http import cookies
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
    """

    auth_token: str | None = None
    auth_token_type: str | None = None
    refresh_token: str | None = None
    api_key: str | None = None

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

        if cookies_header is not None:
            cookie_jar = cookies.SimpleCookie(cookies_header)

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
