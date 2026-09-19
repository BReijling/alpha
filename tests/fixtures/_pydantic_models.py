from __future__ import annotations

from pydantic import BaseModel, PrivateAttr


class PydanticAddress(BaseModel):
    street: str
    house_number: int
    city: str
    _country: str = PrivateAttr()


class PydanticAddressIncorrectType(BaseModel):
    street: str
    house_number: int
    city: str
    country: Type  # type: ignore # noqa: F821
