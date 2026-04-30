from copy import deepcopy
import datetime
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional, Type, TypeVar

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

from . import exceptions

P = TypeVar("P", bound="Pet")


class PetType(Enum):
    NONE = 0
    DOG = auto()
    CAT = auto()
    RABBIT = auto()


@dataclass
class Pet:
    name: str
    pet_type: PetType
    date_of_birth: datetime.date
    weight: Optional[float] = None
    good_boy: Optional[bool] = None
    id: int = field(default=1)

    @property
    def age(self) -> int:
        delta = datetime.date(2022, 2, 2) - self.date_of_birth
        return delta.days // 365

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": 1,
            "name": self.name,
            "pet_type": self.pet_type.name,
            "age": self.age,
            "weight": self.weight,
            "good_boy": self.good_boy,
        }

    @classmethod
    def factory(cls: Type[P], **kwargs) -> P:
        return cls(
            name=kwargs["name"],
            pet_type=PetType[kwargs["pet_type"]],
            date_of_birth=kwargs["date_of_birth"],
            good_boy=kwargs["good_boy"],
        )


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

    def check_dataclass_return_list(self, pet: Pet) -> list[Pet]:
        if isinstance(pet, Pet):
            pet2 = deepcopy(pet)
            pet2.id = 2
            pet2.name = "Dug"
            return [pet, pet2]
        # raise exceptions.InvalidInstance(
        #     "The object is not an instance of Pet"
        # )

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
