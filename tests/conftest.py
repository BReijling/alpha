from dataclasses import dataclass, field
from enum import Enum, auto
import json
from typing import Any

import pytest
from alpha.domain.models.base_model import BaseDomainModel
from alpha.encoder import JSONEncoder
from alpha.factories.request_factory import RequestFactory
from alpha.factories.response_factory import ResponseFactory
from tests.fixtures._api_classes import ApiTrack
from tests.fixtures.fake_factory_classes import FakeTypeFactory


class PetType(Enum):
    DOG = auto()
    CAT = auto()
    RABBIT = auto()


@dataclass
class Pet(BaseDomainModel):
    id: int = field(init=False)
    name: str
    category: PetType
    age: int
    weight: float | None = None
    good_boy: bool | None = None
    remarks: str | None = None


@pytest.fixture
def pet() -> Pet:
    return Pet(
        name="Pluto",
        category=PetType.DOG,
        age=10,
        weight=18.8,
        good_boy=True,
        remarks="Pluto is Mickeys best friend",
    )


@pytest.fixture
def api_track_point():
    return ApiTrack(id=1, latitude=1.0, longitude=1.0, altitude=1)


@pytest.fixture
def encoder_factory():
    def run_encoder(obj, key):
        json_ = json.dumps(obj, cls=JSONEncoder)
        dict_ = json.loads(json_)
        return dict_[key]

    return run_encoder


@pytest.fixture
def request_factory():
    def factory(
        func: Any,
        cast_args: bool,
        use_model_class_factory: bool = True,
    ):
        return RequestFactory(
            func=func,
            cast_args=cast_args,
            use_model_class_factory=use_model_class_factory,
            generic_type_factory=FakeTypeFactory,
            enum_type_factory=FakeTypeFactory,
            json_patch_type_factory=FakeTypeFactory,
        )

    return factory


@pytest.fixture
def response_factory():
    return ResponseFactory()
