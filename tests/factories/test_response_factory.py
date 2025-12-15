from datetime import datetime

import pytest

from alpha import exceptions
from alpha.factories.response_factory import ResponseFactory
from tests.fixtures._api_classes import (
    ApiLesserUserModel,
    ApiTrack,
    ApiTrackListModel,
    ApiTrackModel,
    ApiTrackObjectModel,
    ApiUserModel,
    FakeUserModel,
)
from tests.fixtures._domain_models import Gender
from tests.fixtures.api_generate_models.airplane import Airplane
from tests.fixtures.api_generate_models.flight import Flight
from tests.fixtures.api_generate_models.track import Track
from tests.fixtures.api_generate_models.track_point import TrackPoint


def test_response_factory_process(response_factory: ResponseFactory, response_user):

    result = response_factory.process(response=response_user, cls=FakeUserModel)
    assert isinstance(result, FakeUserModel)
    assert hasattr(result, "username")
    assert hasattr(result, "email")
    assert hasattr(result, "birthday")
    assert hasattr(result, "street")
    assert hasattr(result, "city")
    assert hasattr(result, "gender")
    assert not hasattr(result, "age")


def test_response_factory_lesser_api_model(
    response_factory: ResponseFactory, response_user
):

    result = response_factory.process(response=response_user, cls=ApiLesserUserModel)
    assert isinstance(result, ApiLesserUserModel)
    assert hasattr(result, "username")
    assert hasattr(result, "email")
    assert not hasattr(result, "birthday")
    assert not hasattr(result, "street")
    assert not hasattr(result, "city")
    assert not hasattr(result, "gender")


def test_response_factory_property_call(
    response_factory: ResponseFactory, response_user
):

    result = response_factory.process(response=response_user, cls=ApiUserModel)
    assert isinstance(result, ApiUserModel)
    assert hasattr(result, "age")
    assert result.age == 1
    assert isinstance(result.workdays, list)
    assert result.workdays[0] == 0


def test_response_factory_enum_handling(
    response_factory: ResponseFactory, response_user
):

    assert isinstance(response_user.gender, Gender)
    result = response_factory.process(response=response_user, cls=FakeUserModel)
    assert isinstance(result, FakeUserModel)
    assert result.gender == "MALE"


def test_response_factory_incomplete_response(response_factory, incomplete_track_point):

    with pytest.raises(exceptions.MissingAttributeError):
        response_factory.process(response=incomplete_track_point, cls=ApiTrack)


def test_response_factory_flat_object(response_factory: ResponseFactory, flat_track):

    result = response_factory.process(response=flat_track, cls=ApiTrackModel)
    assert isinstance(result, ApiTrackModel)
    assert result.id == 2


def test_response_factory_nested_object(
    response_factory: ResponseFactory, nested_track
):

    result = response_factory.process(response=nested_track, cls=ApiTrackObjectModel)
    assert isinstance(result, ApiTrackObjectModel)
    assert isinstance(result.track, ApiTrack)
    assert result.id == 3


def test_response_factory_list_attribute(response_factory: ResponseFactory, track):

    result = response_factory.process(response=track, cls=ApiTrackListModel)
    assert isinstance(result, ApiTrackListModel)
    assert isinstance(result.tracks[0], ApiTrack)


def test_response_factory_list_object(
    response_factory: ResponseFactory, track_points, track_point
):

    result = response_factory.process(response=track_points, cls=list[ApiTrack])
    assert isinstance(result, list)
    assert isinstance(result[0], ApiTrack)

    with pytest.raises(exceptions.ClassMismatchException):
        response_factory.process(response=track_point, cls=list[ApiTrack])


def test_response_complex_track_object(
    response_factory: ResponseFactory, track_instance
):

    result = response_factory.process(response=track_instance, cls=Track)
    assert isinstance(result, Track)

    assert isinstance(result.trackpoints, list)
    assert all([isinstance(t, TrackPoint) for t in result.trackpoints])

    assert result.trackpoints[0].latitude == 1.0
    assert result.trackpoints[0].longitude == 1.0
    assert result.trackpoints[0].altitude == 1000
    assert result.trackpoints[0].heading == 301
    assert result.trackpoints[0].timestamp == datetime(2015, 3, 17, 12, 0)

    assert isinstance(result.flight, Flight)
    assert result.flight.departure_icao == "EHGR"
    assert result.flight.departure_time == datetime(2015, 3, 17, 12, 0)
    assert result.flight.arrival_icao == "EHGR"
    assert result.flight.arrival_time == datetime(2015, 3, 17, 13, 0)

    assert isinstance(result.flight.airplane, Airplane)
    assert result.flight.airplane.ac_type == "HELICOPTER"
    assert result.flight.airplane.callsign == "REDSK15"
    assert result.flight.airplane.engine_count == 2
    assert result.flight.airplane.manufacturer == "Boeing"
