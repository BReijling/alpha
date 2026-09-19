from copy import deepcopy
import datetime
from typing import Any
import dateutil
from werkzeug.datastructures import FileStorage

from alpha.exceptions import (
    BadGatewayException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
    GatewayTimeoutException,
    InternalServerErrorException,
    MethodNotAllowedException,
    NotAcceptableException,
    NotFoundException,
    NotImplementedException,
    PayloadTooLargeException,
    ServiceUnavailableException,
    UnauthorizedException,
    UnprocessableContentException,
)
from alpha.utils.openapi_test.models import AttrsPet, Pet, PetType, PydanticPet

from . import exceptions


class TestService:
    @staticmethod
    def hello() -> str:
        return "API is running"

    def is_date(self, obj: Any) -> bool:
        return isinstance(obj, datetime.date)

    def is_datetime(self, obj: Any) -> bool:
        return isinstance(obj, datetime.datetime)

    def check_datetime_tz_utc(self, obj: datetime.datetime) -> bool:
        return obj.tzinfo == dateutil.tz.tz.tzutc()

    def check_datetime_tz_offset(self, obj: datetime.datetime) -> bool:
        return obj.tzinfo == dateutil.tz.tz.tzoffset(None, 7200)

    def is_integer(self, obj: Any) -> bool:
        return isinstance(obj, int)

    def is_float(self, obj: Any) -> bool:
        return isinstance(obj, float)

    def is_list(self, obj: Any) -> bool:
        return isinstance(obj, list)

    def check_dataclass(self, pet: Pet) -> Pet:
        if isinstance(pet, Pet):
            return pet
        raise exceptions.InvalidInstance(
            "The object is not an instance of Pet"
        )

    def check_attrs_class(self, pet: AttrsPet) -> AttrsPet:
        if isinstance(pet, AttrsPet):
            return pet
        raise exceptions.InvalidInstance(
            "The object is not an instance of AttrsPet; received type: "
            f"{type(pet)}"
        )

    def check_pydantic_class(self, pet: PydanticPet) -> PydanticPet:
        if isinstance(pet, PydanticPet):
            return pet
        raise exceptions.InvalidInstance(
            "The object is not an instance of PydanticPet; received type: "
            f"{type(pet)}"
        )

    def check_dataclass_return_list(self, pet: Pet) -> list[Pet]:
        if isinstance(pet, Pet):
            pet2 = deepcopy(pet)
            pet2.id = 2
            pet2.name = "Dug"
            return [pet, pet2]

    def check_attrs_class_return_list(self, pet: AttrsPet) -> list[AttrsPet]:
        if isinstance(pet, AttrsPet):
            pet2 = deepcopy(pet)
            pet2.id = 2
            pet2.name = "Dug"
            return [pet, pet2]

    def check_pydantic_class_return_list(
        self, pet: PydanticPet
    ) -> list[PydanticPet]:
        if isinstance(pet, PydanticPet):
            pet2 = deepcopy(pet)
            pet2.id = 2
            pet2.name = "Dug"
            return [pet, pet2]

    def handle4xx(self, pet: Pet) -> Any:
        if pet.weight and pet.weight < 0:
            raise exceptions.InvalidPetException(
                "This pet has a negative weight!"
            )
        if pet.pet_type == PetType.CAT.name:
            raise exceptions.NoCatsAllowedException(
                "This method does not want to process cats"
            )
        if not pet.good_boy:
            raise exceptions.GoodBoysOnlyException(
                "This method only allows GOOD BOYS!"
            )
        # return pet

    def upload_document(self, files: list[FileStorage]) -> str:
        file = files[0]
        if isinstance(file, FileStorage):
            return file.filename

    def raise_exception(self, code: int) -> None:
        if code == 400:
            raise BadRequestException("Bad request")
        elif code == 401:
            raise UnauthorizedException("Unauthorized")
        elif code == 403:
            raise ForbiddenException("Forbidden")
        elif code == 404:
            raise NotFoundException("Not found")
        elif code == 405:
            raise MethodNotAllowedException("Method not allowed")
        elif code == 406:
            raise NotAcceptableException("Not acceptable")
        elif code == 409:
            raise ConflictException("Conflict")
        elif code == 413:
            raise PayloadTooLargeException("Payload too large")
        elif code == 422:
            raise UnprocessableContentException("Unprocessable content")
        elif code == 500:
            raise InternalServerErrorException("Internal server error")
        elif code == 501:
            raise NotImplementedException("Not implemented")
        elif code == 502:
            raise BadGatewayException("Bad gateway")
        elif code == 503:
            raise ServiceUnavailableException("Service unavailable")
        elif code == 504:
            raise GatewayTimeoutException("Gateway timeout")
        # else:
        #     raise Exception("Unknown exception")
