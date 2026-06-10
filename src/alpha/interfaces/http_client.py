from typing import Protocol, Any, runtime_checkable


@runtime_checkable
class HTTPResponse(Protocol):
    """Interface for HTTP response objects returned by HTTP clients.

    This interface is compatible with the response objects returned by popular
    synchronous HTTP client libraries, for example, the `requests` library,
    `httpx` library or any custom implementation that follows the same
    attributes and method signatures.

    This interface defines the attributes and methods that an HTTP response
    object should have to be compatible with the REST API repository. It
    includes attributes for accessing the response status code, headers, and
    content, as well as a method for parsing the response content as JSON.
    """

    status_code: int
    headers: dict[str, str]
    content: bytes

    def json(self) -> Any: ...
    def text(self) -> str: ...
    def raise_for_status(self) -> None: ...


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

    cookies: dict[str, str]
    headers: dict[str, str]

    def request(
        self, method: str, url: str, **kwargs: Any
    ) -> HTTPResponse: ...
    def close(self) -> None: ...

    def post(
        self, url: str, json: Any = None, **kwargs: Any
    ) -> HTTPResponse: ...
    def get(self, url: str, **kwargs: Any) -> HTTPResponse: ...
    def delete(self, url: str, **kwargs: Any) -> HTTPResponse: ...
    def put(
        self, url: str, json: Any = None, **kwargs: Any
    ) -> HTTPResponse: ...
    def patch(
        self, url: str, json: Any = None, **kwargs: Any
    ) -> HTTPResponse: ...
