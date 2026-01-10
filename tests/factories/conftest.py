"""_summary_"""

from datetime import date, datetime
from typing import Callable

import pytest

from alpha.factories.field_iterator import Field, FieldIterator
from alpha.factories.jwt_factory import JWTFactory
from alpha.infra.models.json_patch import JsonPatch
from tests.fixtures._api_classes import (
    ApiTrack,
    FakeGender,
    FakeUserModel,
)
from tests.fixtures._attrs_models import AttrsAddress
from tests.fixtures._domain_models import (
    Address,
    FlatTrack,
    Gender,
    IncompleteTrackPoint,
    NestedTrack,
    ResponseUser,
    Track,
    TrackPoint,
)
from tests.fixtures._pydantic_models import PydanticAddress
from tests.fixtures.api_generate_models.json_patch import (
    JsonPatch as ApiJsonPatch,
)
from tests.fixtures.class_factories import (
    any_class_factory,
    api_address,
    api_address_nested,
    api_track_model,
    dataclass_class_factory,
    default_field_factory,
    default_fields,
    dict_class_factory,
    enum_class_factory,
    factory_classes,
    fake_all_type_class,
    fake_dataclass,
    fake_dict_factory_class,
    generic_alias_class_factory,
    iterable_class_factory,
    json_patch_class_factory,
    model_class_factory,
    model_class_factory_unit,
    native_class_factory,
    union_class_factory,
)
from tests.fixtures.domain_models import track_models
from tests.fixtures.fake_service_class import FakeService
from tests.fixtures.logging import (
    file_handler,
    file_handler_without_filename,
    rotating_file_handler,
    stream_handler,
    timed_rotating_file_handler,
    watched_file_handler,
)
from tests.fixtures.type_factories import (
    datetime_type_factory,
    enum_type_factory,
    generic_type_factory,
    json_patch_type_factory,
)


@pytest.fixture
def api_user() -> FakeUserModel:
    return FakeUserModel(
        username="Carlos",
        email="info@carlos.com",
        birthday=date(1980, 1, 1),
        street="Avenue de Monte-Carlo",
        city="Monte Carlo",
        gender=FakeGender.MALE,
    )


@pytest.fixture
def response_user() -> ResponseUser:
    return ResponseUser(
        username="name",
        email="info@mail.com",
        birthday=date(2000, 1, 1),
        street="Street 1",
        city="City",
        gender=Gender.MALE,
        workdays=[0, 1, 2, 3, 4],
    )


@pytest.fixture(name="track_point")
def track_point():
    return TrackPoint(id=1, latitude=1.0, longitude=1.0, altitude=1)


@pytest.fixture
def api_track_point():
    return ApiTrack(id=1, latitude=1.0, longitude=1.0, altitude=1)


@pytest.fixture
def incomplete_track_point():
    return IncompleteTrackPoint(id=1, latitude=1.0, longitude=1.0)


@pytest.fixture(name="track_points")
def track_points() -> list[TrackPoint]:
    return [
        TrackPoint(id=1, latitude=1.0, longitude=1.0, altitude=1),
        TrackPoint(id=2, latitude=2.0, longitude=2.0, altitude=2),
        TrackPoint(id=3, latitude=3.0, longitude=3.0, altitude=3),
    ]


@pytest.fixture
def flat_track():
    return FlatTrack(
        id=2, name="flat_track", latitude=2.0, longitude=2.0, altitude=2
    )


@pytest.fixture
def nested_track(track_point: TrackPoint):
    return NestedTrack(id=3, name="nested_track", track=track_point)


@pytest.fixture
def track(track_points: list[TrackPoint]):
    return Track(
        id=1,
        name="track",
        tracks=track_points,
    )


@pytest.fixture
def api_json_patch_add():
    return ApiJsonPatch(op="add", path="/test", value="test")


@pytest.fixture
def api_json_patch_replace():
    return ApiJsonPatch(op="replace", path="/test", value="test")


@pytest.fixture
def api_json_patch_remove():
    return ApiJsonPatch(op="remove", path="/test", value="test")


@pytest.fixture
def str_func():
    def func(obj: str):
        return obj

    return func


@pytest.fixture
def list_func():
    def func(obj: list[str]):
        return obj

    return func


@pytest.fixture
def enum_func():
    def func(obj: Gender):
        return obj

    return func


@pytest.fixture
def dataclass_func():
    def func(obj: TrackPoint):
        return obj

    return func


@pytest.fixture
def json_patch_func():
    def func(obj: JsonPatch):
        return obj

    return func


@pytest.fixture
def track_instance():
    airplane = track_models.Airplane(
        ac_type=track_models.AcType.HELICOPTER,
        callsign="REDSK15",
        engine_count=2,
        manufacturer="Boeing",
    )

    flight = track_models.Flight(
        airplane=airplane,
        departure_icao="EHGR",
        departure_time=datetime(2015, 3, 17, 12, 0),
        arrival_icao="EHGR",
        arrival_time=datetime(2015, 3, 17, 13, 0),
    )

    track = track_models.Track(
        name="test track",
        trackpoints=[
            track_models.TrackPoint(
                latitude=1.0,
                longitude=1.0,
                altitude=1000,
                heading=301,
                timestamp=datetime(2015, 3, 17, 12, 0),
            ),
            track_models.TrackPoint(
                latitude=2.0,
                longitude=2.0,
                altitude=1000,
                heading=301,
                timestamp=datetime(2015, 3, 17, 12, 1),
            ),
            track_models.TrackPoint(
                latitude=3.0,
                longitude=3.0,
                altitude=1000,
                heading=301,
                timestamp=datetime(2015, 3, 17, 12, 2),
            ),
        ],
        flight=flight,
    )
    return track


@pytest.fixture
def flight_with_none_airplane():
    return track_models.Flight(
        airplane=None,
        departure_icao="EHGR",
        departure_time=datetime(2015, 3, 17, 12, 0),
        arrival_icao="EHGR",
        arrival_time=datetime(2015, 3, 17, 13, 0),
    )


@pytest.fixture
def field_iterator_dataclass():
    return FieldIterator(Address)


@pytest.fixture
def field_iterator_attrs():
    return FieldIterator(AttrsAddress)


@pytest.fixture
def field_iterator_pydantic():
    return FieldIterator(PydanticAddress)


@pytest.fixture
def fake_service():
    return FakeService()


@pytest.fixture
def field():
    return Field(init=True, name="test", type_="str", default=None)


@pytest.fixture
def field_iterator_dataclass():
    return FieldIterator(Address)


@pytest.fixture
def field_iterator_attrs():
    return FieldIterator(AttrsAddress)


# JWT fixtures for token factory tests
@pytest.fixture
def jwt_payload():
    return {
        "sub": "user123",
        "name": "John Doe",
        "admin": True,
    }


@pytest.fixture
def jwt_factory_factory() -> Callable[[str, str, int], JWTFactory]:
    def factory(secret: str, issuer: str, lifetime_hours: int) -> JWTFactory:
        return JWTFactory(
            secret=secret,
            issuer=issuer,
            lifetime_hours=lifetime_hours,
            jwt_algorithm="HS256",
        )

    return factory
