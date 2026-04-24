from typing import TYPE_CHECKING, Any, Literal, overload
import json
from alpha.encoder import JSONEncoder
from alpha.utils.cookie import Cookie
from alpha.utils._http_codes import http_codes_en

if TYPE_CHECKING:
    from flask.wrappers import Response
else:
    Response = Any


@overload
def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None,
    data_type: str,
    http_codes: dict[int, tuple[str, str]],
    json_encoder: type[json.JSONEncoder] | None,
    response_type: Literal["dict"],
) -> tuple[dict[str, Any], int]: ...


@overload
def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None,
    data_type: str,
    http_codes: dict[int, tuple[str, str]],
    json_encoder: type[json.JSONEncoder] | None,
    response_type: Literal["flask"],
) -> tuple[Response, int]: ...


@overload
def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None,
    data_type: str,
    http_codes: dict[int, tuple[str, str]],
    json_encoder: type[json.JSONEncoder] | None,
    response_type: None = None,
) -> tuple[dict[str, Any], int]: ...


def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None = None,
    data_type: str = "application/json",
    http_codes: dict[int, tuple[str, str]] = http_codes_en,
    json_encoder: type[json.JSONEncoder] | None = JSONEncoder,
    response_type: str | None = "dict",
) -> tuple[Response, int] | tuple[dict[str, Any], int]:
    """Create a HTTP response object.

    Parameters
    ----------
    status_code
        HTTP status code for the response.
    status_message
        Human-readable message describing the status.
    data
        Additional data to include in the response, by default None
    data_type
        The MIME type of the response, by default "application/json"
    http_codes
        A dictionary mapping HTTP status codes to their descriptions, by
        default http_codes_en
    json_encoder
        A custom JSON encoder class to use when encoding the response data, by
        default alpha.encoder.JSONEncoder
    response_type
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
        "type": data_type or "about:blank",
    }

    if response_type == "flask":
        # Importing Flask's Response class here lazily to avoid unnecessary
        # dependencies when not using Flask.
        from flask.wrappers import Response

        filtered_data, cookies = _split_cookies_from_object(data)

        if filtered_data is not None:
            obj["data"] = filtered_data

        resp = Response(
            response=json.dumps(obj, cls=json_encoder),
            status=status_code,
            mimetype=data_type,
        )

        for cookie in cookies:
            if cookie.operation == "set":
                resp.set_cookie(  # type: ignore
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
                resp.delete_cookie(  # type: ignore
                    key=cookie.key,
                    path=cookie.path,
                    domain=cookie.domain,
                )

        return resp, status_code

    if response_type == "dict":
        if data is not None:
            obj["data"] = data
        return obj, status_code

    raise ValueError("Invalid response type. Must be 'flask' or 'dict'.")


def _split_cookies_from_object(
    obj: Any | None,
) -> tuple[Any | None, list[Cookie]]:
    """Split a response object into its data and cookies.

    Parameters
    ----------
    obj
        The response object containing the data and cookies.

    Returns
    -------
        A tuple containing the data and a list of Cookie objects representing
        the cookies.
    """
    if isinstance(obj, Cookie):
        return None, [obj]
    if isinstance(obj, (list, tuple, set)):
        data: list[Any] = [
            item
            for item in obj
            if not isinstance(item, Cookie)  # type: ignore
        ]
        cookies = [cookie for cookie in obj if isinstance(cookie, Cookie)]  # type: ignore

        if len(data) == 1:
            data = data[0]
        return data, cookies
    return obj, []
