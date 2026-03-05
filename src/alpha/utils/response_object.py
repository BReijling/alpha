from typing import Any, Literal, overload
from flask import Response
from alpha.services.models.cookie import Cookie
from alpha.utils._http_codes import http_codes_en


@overload
def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None,
    data_type: str,
    http_codes: dict[int, tuple[str, str]],
    response_type: Literal["dict"],
) -> tuple[dict[str, Any], int]: ...


@overload
def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None,
    data_type: str,
    http_codes: dict[int, tuple[str, str]],
    response_type: Literal["flask"],
) -> tuple[Response, int]: ...


@overload
def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None = None,
    data_type: str = "application/json",
    http_codes: dict[int, tuple[str, str]] = http_codes_en,
    response_type: None = None,
) -> tuple[dict[str, Any], int]: ...


def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None = None,
    data_type: str = "application/json",
    http_codes: dict[int, tuple[str, str]] = http_codes_en,
    response_type: str | None = "dict",
) -> tuple[Response, int] | tuple[dict[str, Any], int]:
    """Create a HTTP response object.

    Parameters
    ----------
    status_code
        HTTP status code for the response.
    status_message
        Human-readable message describing the status.
    data, optional
        Additional data to include in the response, by default None
    data_type, optional
        The MIME type of the response, by default "application/json"
    http_codes, optional
        A dictionary mapping HTTP status codes to their descriptions, by
        default http_codes_en
    response_type, optional
        The type of response to create, either "flask" or "dict", by default
        "dict"

    Returns
    -------
        A tuple containing the response object and the HTTP status code.
    """
    if response_type is None:
        response_type = "dict"

    obj: dict[str, Any] = {
        "detail": status_message,
        "status": status_code,
        "title": http_codes[status_code][0],
        "type": "about:blank" if not data_type else data_type,
    }

    if data is not None:
        obj["data"] = data

    if response_type == "flask":
        resp = Response(
            response=obj,
            status=status_code,
            mimetype=data_type,
        )

        for cookie in extract_cookies_from_object(data):
            if cookie.operation == "set":
                resp.set_cookie(
                    key=cookie.key,
                    value=cookie.value,
                    max_age=cookie.max_age,
                    expires=cookie.expires,
                    path=cookie.path,
                    domain=cookie.domain,
                    secure=cookie.secure,
                    httponly=cookie.httponly,
                    samesite=cookie.samesite,
                )
            if cookie.operation == "delete":
                resp.delete_cookie(
                    key=cookie.key,
                    path=cookie.path,
                    domain=cookie.domain,
                )

        return resp, status_code

    if response_type == "dict":
        return obj, status_code

    raise ValueError("Invalid response type. Must be 'flask' or 'dict'.")


def extract_cookies_from_object(obj: dict[str, Any]) -> list[Cookie]:
    """Extract Cookie objects from an object.

    Parameters
    ----------
    obj
        The response object containing the cookies.

    Returns
    -------
        A list of Cookie objects representing the cookies.
    """
    if isinstance(obj, Cookie):
        return [obj]
    if isinstance(obj, list | tuple | set):
        return [cookie for cookie in obj if isinstance(cookie, Cookie)]
    return []
