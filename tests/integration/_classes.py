from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto
from typing import ClassVar

import sqlalchemy as sa
from sqlalchemy.orm import registry

from alpha.domain.models.base_model import BaseDomainModel


class PetType(Enum):
    DOG = auto()
    CAT = auto()
    RABBIT = auto()
    DUCK = auto()
    FOX = auto()


@dataclass
class Pet(BaseDomainModel):
    id: int = field(compare=False)
    name: str
    pet_type: PetType
    date_of_birth: date
    weight: float | None = field(compare=False, default=None)
    good_boy: bool | None = field(compare=False, default=None)
    remarks: str | None = field(compare=False, default=None)


@dataclass
class Owner(BaseDomainModel):
    id: int = field(compare=False)
    name: str
    pet: Pet


class FakeMapper:
    started: ClassVar[bool] = False

    schema_name: ClassVar[str] = "ddd"

    mapper_registry: ClassVar = registry()

    convention: ClassVar = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    reflect_engine: ClassVar[sa.Engine | None] = None
    metadata: ClassVar = sa.MetaData(naming_convention=convention)
    if reflect_engine:
        metadata.reflect(bind=reflect_engine)

    pets = sa.Table(
        "pets",
        metadata,
        sa.Column("id", sa.INTEGER, primary_key=True, unique=True),
        sa.Column("name", sa.VARCHAR(20), primary_key=True),
        sa.Column("pet_type", sa.Enum(PetType), nullable=False),
        sa.Column("good_boy", sa.BOOLEAN, nullable=True, default=False),
        sa.Column("date_of_birth", sa.DATE, nullable=False),
        sa.Column("weight", sa.DOUBLE_PRECISION, nullable=True),
        sa.Column("remarks", sa.VARCHAR(200), nullable=True),
        sa.UniqueConstraint("name", "pet_type"),
    )

    @classmethod
    def start_mapping(cls):
        cls.mapper_registry.map_imperatively(Pet, cls.pets)

        cls.started = True
