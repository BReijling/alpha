from datetime import date
from typing import Any, List


class Model:
    openapi_types: dict[str, type] = {}
    attribute_map: dict[str, str] = {}

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__

    def to_str(self):
        return

    def __repr__(self):
        return

    def __eq__(self, other):
        return

    def __ne__(self, other):
        return


class FakeGender(Model):
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNKNOWN = "UNKNOWN"

    def __init__(self):  # noqa: E501
        self.openapi_types = {}
        self.attribute_map = {}


class FakeUserModel(Model):
    def __init__(
        self,
        username: Any = None,
        email: Any = None,
        birthday: Any = None,
        street: Any = None,
        city: Any = None,
        gender: Any = None,
    ):
        self.openapi_types = {
            'username': str,
            'email': str,
            'birthday': date,
            'street': str,
            'city': str,
            'gender': FakeGender,
        }

        self.attribute_map = {
            'username': 'username',
            'email': 'email',
            'birthday': 'birthday',
            'street': 'street',
            'city': 'city',
            'gender': 'gender',
        }

        self.username = username
        self.email = email
        self.birthday = birthday
        self.street = street
        self.city = city
        self.gender = gender

    @property
    def username(self) -> Any:
        return self._username

    @username.setter
    def username(self, username: Any):
        self._username = username

    @property
    def email(self) -> Any:
        return self._email

    @email.setter
    def email(self, email: Any):
        self._email = email

    @property
    def birthday(self):
        return self._birthday

    @birthday.setter
    def birthday(self, birthday: Any):
        self._birthday = birthday

    @property
    def street(self) -> Any:
        return self._street

    @street.setter
    def street(self, street: Any):
        self._street = street

    @property
    def city(self) -> Any:
        return self._city

    @city.setter
    def city(self, city: Any):
        self._city = city

    @property
    def gender(self) -> Any:
        return self._gender

    @gender.setter
    def gender(self, gender: Any):
        self._gender = gender


class ApiUserModel(FakeUserModel):
    def __init__(
        self,
        username: Any = None,
        email: Any = None,
        birthday: Any = None,
        street: Any = None,
        city: Any = None,
        gender: Any = None,
        age: Any = None,
        workdays: Any = None,
    ):
        self.openapi_types = {
            'username': str,
            'email': str,
            'birthday': date,
            'street': str,
            'city': str,
            'gender': FakeGender,
            'age': int,
            'workdays': List[int],
        }

        self.attribute_map = {
            'username': 'username',
            'email': 'email',
            'birthday': 'birthday',
            'street': 'street',
            'city': 'city',
            'gender': 'gender',
            'age': 'age',
            'workdays': 'workdays',
        }

        self.username = username
        self.email = email
        self.birthday = birthday
        self.street = street
        self.city = city
        self.gender = gender
        self.age = age
        self.workdays = workdays

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, age: Any):
        self._age = age

    @property
    def workdays(self):
        return self._workdays

    @workdays.setter
    def workdays(self, workdays):
        self._workdays = workdays


class ApiLesserUserModel(Model):
    def __init__(
        self,
        username: Any = None,
        email: Any = None,
    ):
        self.openapi_types = {
            'username': str,
            'email': str,
        }

        self.attribute_map = {
            'username': 'username',
            'email': 'email',
        }

        self.username = username
        self.email = email

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username: Any):
        self._username = username

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email: Any):
        self._email = email


class FakeAddressModel(Model):
    def __init__(
        self,
        street: Any = None,
        house_number: Any = None,
        city: Any = None,
    ):
        self.openapi_types = {
            'street': str,
            'house_number': int,
            'city': str,
        }

        self.attribute_map = {
            'street': 'street',
            'house_number': 'house_number',
            'city': 'city',
        }

        self.street = street
        self.house_number = house_number
        self.city = city

    @property
    def street(self):
        return self._street

    @street.setter
    def street(self, street: Any):
        self._street = street

    @property
    def house_number(self):
        return self._house_number

    @house_number.setter
    def house_number(self, house_number: Any):
        self._house_number = house_number

    @property
    def city(self):
        return self._city

    @city.setter
    def city(self, city: Any):
        self._city = city


class FakeAddressNested(Model):
    def __init__(self, address: Any = None):
        self.openapi_types = {'address': FakeAddressModel}
        self.attribute_map = {'address': 'address'}

        self.address = address

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address: Any):
        self._address = address


class ApiTrack(Model):
    def __init__(
        self,
        id: Any = None,
        latitude: Any = None,
        longitude: Any = None,
        altitude: Any = None,
    ):
        self.openapi_types = {
            'id': int,
            'latitude': float,
            'longitude': float,
            'altitude': float,
        }
        self.attribute_map = {
            'id': 'id',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'altitude': 'altitude',
        }

        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: Any):
        self._id = id

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, latitude: Any):
        self._latitude = latitude

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, longitude: Any):
        self._longitude = longitude

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, altitude: Any):
        self._altitude = altitude


class ApiTrackModel(Model):
    def __init__(
        self,
        id: Any = None,
        name: Any = None,
        latitude: Any = None,
        longitude: Any = None,
        altitude: Any = None,
    ):
        self.openapi_types = {
            'id': int,
            'name': str,
            'latitude': float,
            'longitude': float,
            'altitude': float,
        }
        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'altitude': 'altitude',
        }

        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: Any):
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: Any):
        self._name = name

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, latitude: Any):
        self._latitude = latitude

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, longitude: Any):
        self._longitude = longitude

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, altitude: Any):
        self._altitude = altitude


class ApiTrackObjectModel(Model):
    def __init__(self, id: Any = None, name: Any = None, track: Any = None):
        self.openapi_types = {
            'id': int,
            'name': str,
            'track': ApiTrack,
        }
        self.attribute_map = {'id': 'id', 'name': 'name', 'track': 'track'}

        self.id = id
        self.name = name
        self.track = track

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: Any):
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: Any):
        self._name = name

    @property
    def track(self):
        return self._track

    @track.setter
    def track(self, track: Any):
        self._track = track


class ApiTrackListModel(Model):
    def __init__(self, id: Any = None, name: Any = None, tracks: Any = None):
        self.openapi_types = {
            'id': int,
            'name': str,
            'tracks': list[ApiTrack],
        }
        self.attribute_map = {'id': 'id', 'name': 'name', 'tracks': 'tracks'}

        self.id = id
        self.name = name
        self.tracks = tracks

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: Any):
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: Any):
        self._name = name

    @property
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, tracks: Any):
        self._tracks = tracks
