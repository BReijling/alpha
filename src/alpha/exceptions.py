# HTTP Exceptions
class BadRequestException(Exception):
    """Equivalent to HTTP code 400"""


class UnauthorizedException(Exception):
    """Equivalent to HTTP code 401"""


class ForbiddenException(Exception):
    """Equivalent to HTTP code 403"""


class NotFoundException(Exception):
    """Equivalent to HTTP code 404"""


class NotAcceptableException(Exception):
    """Equivalent to HTTP code 406"""


class ConflictException(Exception):
    """Equivalent to HTTP code 409"""


class PayloadTooLargeException(Exception):
    """Equivalent to HTTP code 413"""


class UnprocessableContentException(Exception):
    """Equivalent to HTTP code 422"""


class ErrorException(Exception): ...


class InternalServerErrorException(ErrorException):
    """Equivalent to HTTP code 500"""


class NotImplementedException(ErrorException):
    """Equivalent to HTTP code 501"""


class BadGatewayException(ErrorException):
    """Equivalent to HTTP code 502"""


class ServiceUnavailableException(ErrorException):
    """Equivalent to HTTP code 503"""


## Common exceptions
class DatabaseMapperError(Exception): ...


class DatabaseSessionError(InternalServerErrorException): ...


class InstrumentedAttributeMissing(Exception): ...


class AlreadyExistsException(ForbiddenException): ...


class TypingFactoryException(Exception): ...


class ModelClassFactoryException(Exception): ...


class DefaultFactoryException(Exception): ...


class ObjectConversionNotSupported(Exception): ...


class ObjectConversionNotAllowed(Exception): ...


class ObjectConversionError(Exception): ...


class UnionArgumentError(Exception): ...


class MixedArgumentTypesError(Exception): ...


class MissingAttributeError(Exception): ...


class ClassMismatchException(Exception): ...


class LoggingHandlerException(Exception): ...


class ClassFactoryException(Exception): ...
