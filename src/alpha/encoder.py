import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, time
from enum import Enum
from json import encoder
from typing import Any
from uuid import UUID

import numpy as np
import pandas as pd
import six

from alpha.interfaces.openapi_model import OpenAPIModel


class JSONEncoder(encoder.JSONEncoder):
    include_nulls = False

    def default(self, o: Any) -> Any:
        if isinstance(o, list):
            return [self.default(item) for item in o]  # type: ignore
        if isinstance(o, OpenAPIModel):
            dikt: dict[str, Any] = {}
            for attr, _ in six.iteritems(o.openapi_types):
                value = getattr(o, attr)
                if value is None and not self.include_nulls:
                    continue
                attr = o.attribute_map[attr]
                dikt[attr] = value
            return dikt
        if hasattr(o, "to_dict"):
            return o.to_dict()
        if hasattr(o, "to_list"):
            return o.to_list()
        if isinstance(o, set):
            return list(o)  # type: ignore
        if isinstance(o, Enum):
            return o.name
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, np.int64):  # type: ignore
            return int(o)
        if isinstance(o, np.float32):  # type: ignore
            return float(o)
        if isinstance(o, pd.Timestamp):
            return o.isoformat()
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, time):
            return o.isoformat()
        if is_dataclass(o):
            if isinstance(o, type):
                cls = getattr(o, "__class__")
                return cls.__name__
            return asdict(o)

        try:
            return json.JSONEncoder.default(self, o)
        except Exception:
            return None
