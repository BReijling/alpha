from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto

from alpha.domain.models.base_model import BaseDomainModel


class Gender(Enum):
    """_summary_"""

    MALE = auto()
    FEMALE = auto()
    UNKNOWN = auto()


class CarType(Enum):
    """_summary_"""

    NONE = 0
    SEDAN = auto()
    COUPE = auto()
    STATION = auto()


@dataclass
class Address(BaseDomainModel):
    """_summary_"""

    street: str
    house_number: int
    city: str


@dataclass
class Car(BaseDomainModel):
    """_summary_"""

    brand: str
    car_type: CarType
    cylinders: int
    weight: float


@dataclass
class User(BaseDomainModel):
    """_summary_"""

    username: str
    address: Address
    birthday: date
    email: str = ""
    gender: Gender = field(default=Gender.UNKNOWN)
    cars: list[Car] = field(default_factory=list)


@dataclass
class ResponseUser(BaseDomainModel):
    """_summary_"""

    username: str
    email: str
    birthday: date
    street: str
    city: str
    gender: Gender
    workdays: list[int]

    @property
    def age(self) -> int:
        """_summary_"""
        return 1


@dataclass
class TrackPoint(BaseDomainModel):
    id: int
    latitude: float
    longitude: float
    altitude: float


@dataclass
class IncompleteTrackPoint(BaseDomainModel):
    id: int
    latitude: float
    longitude: float


@dataclass
class FlatTrack(TrackPoint):
    name: str


@dataclass
class NestedTrack(BaseDomainModel):
    id: int
    name: str
    track: TrackPoint


@dataclass
class Track(BaseDomainModel):
    id: int
    name: str
    tracks: list[TrackPoint]
