from typing import Protocol, Any, runtime_checkable


@runtime_checkable
class HTTPClient(Protocol):
    """Interface for HTTP clients like requests, httpx or a custom
    implementation.

    This interface is compatible with the popular synchronous HTTP client
    libraries, for example, the `requests` library, `httpx` library or any
    custom implementation that follows the same method signatures.

    This interface defines the methods that an HTTP client should implement to
    be compatible with the REST API repository. It includes methods for making
    HTTP requests (POST, GET, DELETE, PUT, PATCH) and allows for additional
    parameters to be passed as needed.
    """

    cookies: Any
    headers: Any

    def post(self, url: str, json: Any = None, **kwargs: Any) -> Any: ...
    def get(self, url: str, **kwargs: Any) -> Any: ...
    def delete(self, url: str, **kwargs: Any) -> Any: ...
    def put(self, url: str, json: Any = None, **kwargs: Any) -> Any: ...
    def patch(self, url: str, json: Any = None, **kwargs: Any) -> Any: ...
