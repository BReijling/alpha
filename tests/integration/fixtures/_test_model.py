from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum, auto
from uuid import UUID


class Enumeration(Enum):
    FIRST = auto()
    SECOND = auto()


@dataclass
class FlatObject:
    text: str
    number: float


@dataclass
class NestedObject:
    single_str: str
    flat_object: FlatObject
    list_of_flat_objects: list[FlatObject]


@dataclass
class TestModel:
    single_str: str
    single_complex: complex
    single_int: int
    single_float: float
    single_bool: bool
    single_uuid: UUID
    single_date: date
    single_datetime: datetime
    single_enum: Enumeration
    flat_object: FlatObject
    nested_object: NestedObject
    list_of_flat_objects: list[FlatObject]
    list_of_nested_objects: list[NestedObject]
    list_of_str: list[str]
    list_of_int: list[int]
    list_of_float: list[float]
    tuple_of_str: tuple[str]
    tuple_of_int: tuple[int]
    tuple_of_float: tuple[float]
    set_of_str: set[str]
    set_of_int: set[int]
    set_of_float: set[float]
    single_dict: dict[str, str]
