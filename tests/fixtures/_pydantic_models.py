from __future__ import annotations

from pydantic import BaseModel


class PydanticAddress(BaseModel):
    street: str
    house_number: int
    city: str


class PydanticAddressIncorrectType(BaseModel):
    street: str
    house_number: int
    city: str
    country: Type
