from __future__ import annotations

from attrs import define


@define
class AttrsAddress:
    street: str
    house_number: int
    city: str


@define
class AttrsAddressIncorrectType:
    street: str
    house_number: int
    city: str
    country: Type
