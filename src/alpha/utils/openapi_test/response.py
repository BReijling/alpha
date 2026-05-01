from typing import Any


def custom_response_builder(
    status_code: int,
    **kwargs: Any,
) -> tuple[dict[str, Any], int]:
    """Custom response builder for testing purposes."""
    return {
        "status_code": status_code,
        **kwargs,
    }, status_code
