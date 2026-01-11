# HTTP Exceptions
class ClientErrorException(Exception):
    """Base class for client-side HTTP exceptions (4xx)."""


class BadRequestException(ClientErrorException):
    """Equivalent to HTTP code 400"""


class UnauthorizedException(ClientErrorException):
    """Equivalent to HTTP code 401"""


class ForbiddenException(ClientErrorException):
    """Equivalent to HTTP code 403"""


class NotFoundException(ClientErrorException):
    """Equivalent to HTTP code 404"""


class NotAcceptableException(ClientErrorException):
    """Equivalent to HTTP code 406"""


class ConflictException(ClientErrorException):
    """Equivalent to HTTP code 409"""


class PayloadTooLargeException(ClientErrorException):
    """Equivalent to HTTP code 413"""


class UnprocessableContentException(ClientErrorException):
    """Equivalent to HTTP code 422"""


class ServerErrorException(Exception):
    """Base class for server-side HTTP exceptions (5xx)."""


class InternalServerErrorException(ServerErrorException):
    """Equivalent to HTTP code 500"""


class NotImplementedException(ServerErrorException):
    """Equivalent to HTTP code 501"""


class BadGatewayException(ServerErrorException):
    """Equivalent to HTTP code 502"""


class ServiceUnavailableException(ServerErrorException):
    """Equivalent to HTTP code 503"""


# General Exceptions
class MissingConfigurationException(Exception):
    """Raised when a required configuration is missing."""


class MissingDependencyException(Exception):
    """Raised when a required dependency is missing."""


# Database exceptions
class DatabaseMapperError(Exception):
    """Raised when there is an error in the database mapping process."""


class DatabaseSessionError(InternalServerErrorException):
    """Raised when there is an error with the database session."""


# ORM Related Exceptions
class InstrumentedAttributeMissing(Exception):
    """Raised when an expected instrumented attribute is missing in the ORM model."""


class AlreadyExistsException(ForbiddenException):
    """Raised when attempting to create a resource that already exists."""


# Factory Related Exceptions
class TypingFactoryException(Exception):
    """Raised when there is an error in the typing factory process."""


class ModelClassFactoryException(Exception):
    """Raised when there is an error in the model class factory process."""


class DefaultFactoryException(Exception):
    """Raised when there is an error in the default factory process."""


class ObjectConversionNotSupported(Exception):
    """Raised when object conversion is not supported for the given type."""


class ObjectConversionNotAllowed(Exception):
    """Raised when object conversion is not allowed for the given type."""


class ObjectConversionError(Exception):
    """Raised when there is an error during object conversion."""


class UnionArgumentError(Exception):
    """Raised when there is an error with union type arguments."""


class MixedArgumentTypesError(Exception):
    """Raised when mixed argument types are provided where not allowed."""


class MissingAttributeError(Exception):
    """Raised when a required attribute is missing from an object."""


class ClassMismatchException(Exception):
    """Raised when there is a mismatch between expected and actual class types."""


class LoggingHandlerException(Exception):
    """Raised when there is an error with logging handlers."""


class ClassFactoryException(Exception):
    """Raised when there is an error in the class factory process."""


# Identity Exceptions
class IdentityError(Exception):
    """Raised when there is a general identity-related error."""


class UserNotFoundException(UnauthorizedException):
    """Raised when a user is not found during authentication."""


class InvalidCredentialsException(UnauthorizedException):
    """Raised when provided credentials are invalid."""


class NotSupportedException(ForbiddenException):
    """Raised when an operation is not supported by the identity provider."""


class InsufficientPermissionsException(ForbiddenException):
    """Raised when the identity lacks sufficient permissions for an operation."""


# Token Exceptions
class TokenError(Exception):
    """Raised when there is a general token-related error."""


class TokenExpiredException(UnauthorizedException):
    """Raised when a token has expired."""


class InvalidSignatureException(UnauthorizedException):
    """Raised when a token has an invalid signature."""


class InvalidTokenException(UnauthorizedException):
    """Raised when a token is invalid."""


class TokenPayloadException(Exception):
    """Raised when there is an error with the token payload."""


class TokenCreationException(Exception):
    """Raised when there is an error during token creation."""


# Cli Exceptions
class InvalidArgumentsException(Exception):
    """Raised when invalid arguments are provided to a CLI command."""
