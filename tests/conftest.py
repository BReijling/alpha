from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
import json
from typing import Any

import pytest
from alpha.domain.models.base_model import BaseDomainModel
from alpha.domain.models.group import Group
from alpha.domain.models.user import User
from alpha.encoder import JSONEncoder
from alpha.factories.jwt_factory import JWTFactory
from alpha.factories.password_factory import PasswordFactory
from alpha.factories.request_factory import RequestFactory
from alpha.factories.response_factory import ResponseFactory
from alpha.providers.models.identity import Identity
from tests.fixtures._api_classes import ApiTrack
from tests.fixtures.fake_factory_classes import FakeTypeFactory
from tests.fixtures.fake_uow_repositories import (
    FakeAuthenticationServiceUserRepository,
    FakeDatabaseProviderGroupRepository,
    FakeDatabaseProviderUserRepository,
    FakeDatabaseProviderUserRepositoryNoUser,
    FakeRefreshTokenRepository,
    FakeUnitOfWork,
)


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


# JWT fixtures for token factory tests
@pytest.fixture
def jwt_secret():
    return "supersecretkey"


@pytest.fixture
def jwt_issuer():
    return "http://localhost"


@pytest.fixture
def jwt_lifetime_hours():
    return 12


@pytest.fixture
def jwt_factory(
    jwt_secret,
    jwt_issuer,
    jwt_lifetime_hours,
) -> JWTFactory:
    return JWTFactory(
        secret=jwt_secret,
        issuer=jwt_issuer,
        lifetime_hours=jwt_lifetime_hours,
        jwt_algorithm="HS256",
    )


@pytest.fixture
def identity() -> Identity:
    return Identity(
        subject="user123",
        username="testuser",
        email="testuser@example.com",
        display_name="Test User",
        groups=["group1", "group2"],
        permissions=["read", "write"],
        claims={"role": "admin"},
        issued_at=datetime.now(tz=timezone.utc),
        expires_at=datetime(3000, 1, 1, tzinfo=timezone.utc),
        role="SUPERUSER",
        audience=None,
        admin=False,
        pretend_identity=None,
    )


@pytest.fixture
def fake_authentication_service_repository():
    return FakeAuthenticationServiceUserRepository()


@pytest.fixture
def fake_database_provider_user_repository():
    return FakeDatabaseProviderUserRepository(
        [
            User(
                id=1,
                username="test_user",
                password=PasswordFactory().hash_password("test_password"),
                email="test_user@example.com",
            )
        ]
    )


@pytest.fixture
def fake_database_provider_user_repository_empty_password():
    return FakeDatabaseProviderUserRepository(
        [
            User(
                id=1,
                username="test_user",
                password=None,
                email="test_user@example.com",
            )
        ]
    )


@pytest.fixture
def fake_database_provider_user_repository_no_user():
    return FakeDatabaseProviderUserRepositoryNoUser()


@pytest.fixture
def fake_database_provider_group_repository():
    return FakeDatabaseProviderGroupRepository(
        [
            Group(
                id=1,
                name="group1",
                permissions=["read", "write"],
                description="A test group",
            ),
            Group(
                id=5,
                name="group5",
                permissions=["append", "create"],
                description="Another test group",
            ),
            Group(
                id=6,
                name="group6",
                permissions=["admin"],
                description="Admin test group",
            ),
        ]
    )


@pytest.fixture
def fake_refresh_token_repository():
    return FakeRefreshTokenRepository()


@pytest.fixture
def fake_uow(
    fake_authentication_service_repository,
    fake_database_provider_user_repository,
    fake_database_provider_user_repository_empty_password,
    fake_database_provider_user_repository_no_user,
    fake_database_provider_group_repository,
    fake_refresh_token_repository,
):
    return FakeUnitOfWork(
        authentication_service=fake_authentication_service_repository,
        database_provider=fake_database_provider_user_repository,
        database_provider_empty_password=fake_database_provider_user_repository_empty_password,
        database_provider_no_user=fake_database_provider_user_repository_no_user,
        users=fake_database_provider_user_repository,
        groups=fake_database_provider_group_repository,
        refresh_tokens=fake_refresh_token_repository,
    )


@pytest.fixture
def password_factory():
    return PasswordFactory()
