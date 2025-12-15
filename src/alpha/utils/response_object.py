from typing import Any

from alpha.utils._http_codes import http_codes_en


def create_response_object(
    status_code: int,
    status_message: str,
    data: Any | None = None,
    data_type: str = "application/json",
    http_codes: dict[int, tuple[str, str]] = http_codes_en,
) -> tuple[dict[str, Any], int]:
    obj = {
        "detail": status_message,
        "status": status_code,
        "title": http_codes[status_code][0],
        "type": "about:blank" if not data_type else data_type,
    }

    if data is not None:
        obj["data"] = data

    return (
        obj,
        status_code,
    )
