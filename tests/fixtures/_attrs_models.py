from __future__ import annotations

from attrs import define, field


@define
class AttrsAddress:
    street: str
    house_number: int
    city: str
    country: str = field(init=False)


@define
class AttrsAddressIncorrectType:
    street: str
    house_number: int
    city: str
    country: Type
