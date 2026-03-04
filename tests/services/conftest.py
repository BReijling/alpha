import pytest

from alpha.domain.models.user import User
from alpha.providers.models.credentials import PasswordCredentials
from alpha.services.authentication_service import AuthenticationService
from tests.fixtures.fake_provider import FakeIdentityProvider


@pytest.fixture
def fake_static_user() -> User:
    return User(
        username="static_user",
        password="static_password",
        email="static_user@example.com",
    )


@pytest.fixture
def static_user_credentials(fake_static_user: User):
    return PasswordCredentials(
        username=fake_static_user.username,
        password=fake_static_user.password,
    )


@pytest.fixture
def fake_user_credentials():
    return PasswordCredentials(
        username="fake_user",
        password="fake_password",
    )


@pytest.fixture
def fake_identity_provider():
    return FakeIdentityProvider()


@pytest.fixture
def authentication_service(
    fake_uow, fake_static_user, fake_identity_provider
) -> AuthenticationService:
    return AuthenticationService(
        identity_provider=fake_identity_provider,
        uow=fake_uow,
        users_repository_name="authentication_service",
        static_user=fake_static_user,
    )
