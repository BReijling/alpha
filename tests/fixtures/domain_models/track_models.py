from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from uuid import UUID, uuid4

from alpha.domain.models.base_model import BaseDomainModel


class AcType(Enum):
    NONE = 0
    FIXED_WING = auto()
    HELICOPTER = auto()


@dataclass
class TrackPoint(BaseDomainModel):
    latitude: float
    longitude: float
    altitude: float
    heading: float
    timestamp: datetime


@dataclass
class Airplane(BaseDomainModel):
    ac_type: AcType
    callsign: str
    engine_count: int
    manufacturer: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class Flight(BaseDomainModel):
    airplane: Airplane | None
    departure_time: datetime
    arrival_time: datetime
    departure_icao: str
    arrival_icao: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class Track(BaseDomainModel):
    name: str
    trackpoints: list[TrackPoint]
    flight: Flight
    id: UUID = field(default_factory=uuid4)
