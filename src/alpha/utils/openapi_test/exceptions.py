from alpha import exceptions


class InvalidInstance(Exception):
    pass


class InvalidPetException(exceptions.BadRequestException):
    pass


class NoCatsAllowedException(exceptions.ForbiddenException):
    pass


class GoodBoysOnlyException(exceptions.UnprocessableContentException):
    pass
