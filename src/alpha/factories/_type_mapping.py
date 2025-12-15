"""Contains the TYPES constant to determine which TypeFactory can be used to
process a certain object type
"""

import datetime
import uuid

from alpha.factories.type_factories import (
    DatetimeTypeFactory,
    GenericTypeFactory,
)
from alpha.interfaces.factories import TypeFactory

TYPES: dict[type, type[TypeFactory]] = {
    str: GenericTypeFactory,
    complex: GenericTypeFactory,
    int: GenericTypeFactory,
    float: GenericTypeFactory,
    bytes: GenericTypeFactory,
    bytearray: GenericTypeFactory,
    list: GenericTypeFactory,
    dict: GenericTypeFactory,
    set: GenericTypeFactory,
    tuple: GenericTypeFactory,
    bool: GenericTypeFactory,
    uuid.UUID: GenericTypeFactory,
    datetime.datetime: DatetimeTypeFactory,
    datetime.date: DatetimeTypeFactory,
}
