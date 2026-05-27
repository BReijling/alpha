import json
from typing import TYPE_CHECKING, Any, Literal, overload

from alpha.utils._http_codes import http_codes_en
from alpha.utils.cookie import Cookie

if TYPE_CHECKING:
    from flask.wrappers import Response
else:
    Response = Any


@overload
def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None,
    accept_header: str,
    supported_data_types: list[str] | None,
    http_codes: dict[int, tuple[str, str]],
    json_encoder: type[json.JSONEncoder] | None,
    response_format: Literal["dict"],
    **kwargs: Any,
) -> tuple[dict[str, Any], int]: ...


@overload
def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None,
    accept_header: str,
    supported_data_types: list[str] | None,
    http_codes: dict[int, tuple[str, str]],
    json_encoder: type[json.JSONEncoder] | None,
    response_format: Literal["flask"],
    **kwargs: Any,
) -> tuple[Response, int]: ...


@overload
def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None,
    accept_header: str,
    supported_data_types: list[str] | None,
    http_codes: dict[int, tuple[str, str]],
    json_encoder: type[json.JSONEncoder] | None,
    response_format: None = None,
    **kwargs: Any,
) -> tuple[dict[str, Any], int]: ...


def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None = None,
    accept_header: str = "application/json",
    supported_data_types: list[str] | None = None,
    http_codes: dict[int, tuple[str, str]] = http_codes_en,
    json_encoder: type[json.JSONEncoder] | None = None,
    response_format: str | None = "dict",
    **kwargs: Any,
) -> tuple[Response, int] | tuple[dict[str, Any], int]:
    """Create a HTTP response object.

    The response object can be either a dictionary or a Flask Response object,
    depending on the value of `response_format`. The response will include the
    status code, a human-readable message, and optionally additional data.
    Only supports JSON responses. For other types, use custom function with
    x-alpha-custom-response-builder in the OpenAPI specification.

    Parameters
    ----------
    status_code
        HTTP status code for the response.
    status_message
        Human-readable message describing the status.
    data
        Additional data to include in the response, by default None
    accept_header
        The value of the Accept header from the request,
        by default "application/json"
    supported_data_types
        A list of supported MIME types for the data_type parameter.
    http_codes
        A dictionary mapping HTTP status codes to their descriptions, by
        default http_codes_en
    json_encoder
        A custom JSON encoder class to use when encoding the response data, by
        default None. If None, the default JSONEncoder will be used.
    response_format
        The type of response to create, either "flask" or "dict", by default
        "dict"

    Returns
    -------
    tuple[dict[str, Any], int]
        A tuple containing the response object as a dictionary and the HTTP
        status code. When response_format is "dict".
    tuple[Response, int]
        A tuple containing the flask.Response object and the HTTP status code.
        When response_format is "flask".
    """
    data_type = _resolve_data_type(accept_header, supported_data_types)

    if response_format is None:
        response_format = "dict"

    if json_encoder is None:
        # Lazily import to avoid circular import during alpha package init.
        from alpha.encoder import JSONEncoder

        json_encoder = JSONEncoder

    obj: dict[str, Any] = {
        "detail": status_message,
        "status": status_code,
        "title": http_codes[status_code][0],
        "type": data_type or "about:blank",
    }

    if response_format == "flask":
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

    if response_format == "dict":
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
    tuple[Any | None, list[Cookie]]
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


def _resolve_data_type(
    accept_header: str | None,
    supported_data_types: list[str] | None,
    default: str = "application/json",
) -> str:
    """Resolve the data type for the response by matching against the supported
    types.

    Match wildcards like "*/*" or "application/*" with first match in supported
    types. If the data type is not supported, resort to default type.

    Parameters
    ----------
    accept_header
        The Accept header from the request.
    supported_data_types
        A list of supported MIME types. If None, all types are supported.
    default
        The default MIME type to use if the provided accept_header is not
        supported.

    Returns
    -------
    str
        The resolved MIME type to use for the response.
    """
    # If no data type provided or no supported types, return default
    if not accept_header or not supported_data_types:
        return default
    # Return provided type if it matches supported type
    if accept_header.lower() in supported_data_types:
        return accept_header.lower()
    # If MIME type wildcard is provided, return first supported type
    if accept_header.startswith("*/"):
        return supported_data_types[0]
    # If MIME subtype is a wildcard, match prefix
    if accept_header.endswith("/*"):
        prefix = accept_header.split("/")[0].lower()
        for supported in supported_data_types:
            if supported.startswith(prefix):
                return supported
    # If not matched, return default
    return default
