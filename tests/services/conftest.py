import pytest

from alpha.services.authentication_service import AuthenticationService


@pytest.fixture
def authentication_service(fake_uow) -> AuthenticationService:
    return AuthenticationService(
        identity_provider=None,
        uow=fake_uow,
        users_repository_name="authentication_service",
    )
