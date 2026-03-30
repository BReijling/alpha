from datetime import datetime, timedelta, timezone
import json

import pytest

from alpha.domain.models.user import User
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token
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
def identity_for_groups() -> Identity:
    return Identity(
        subject="fake_user",
        username="fake_user",
        display_name="Fake User",
        email="test@test.nl",
        groups=["group1", "group2", "group5", "group6"],
        permissions=["read", "write"],
        claims={},
        issued_at=datetime.now(tz=timezone.utc),
    )


@pytest.fixture
def authentication_service(
    fake_uow, fake_static_user, fake_identity_provider
) -> AuthenticationService:
    return AuthenticationService(
        identity_provider=fake_identity_provider,
        uow=fake_uow,
        users_repository_name="authentication_service",
        static_user=fake_static_user,
        refresh_token_storage="test",
    )


@pytest.fixture
def authentication_service_merge_groups(
    fake_uow, fake_static_user, fake_identity_provider
) -> AuthenticationService:
    return AuthenticationService(
        identity_provider=fake_identity_provider,
        uow=fake_uow,
        users_repository_name="authentication_service",
        static_user=fake_static_user,
        merge_with_database_users=True,
        merge_with_database_groups=True,
    )


@pytest.fixture
def authentication_service_use_cookies(
    fake_uow, fake_static_user, fake_identity_provider
) -> AuthenticationService:
    return AuthenticationService(
        identity_provider=fake_identity_provider,
        uow=fake_uow,
        users_repository_name="authentication_service",
        static_user=fake_static_user,
        use_cookies=True,
    )


@pytest.fixture
def fake_refresh_token() -> Token:
    return Token(
        value="fake_refresh_token",
        token_type="Refresh",
        subject="static_user",
        expires_at=datetime.now(tz=timezone.utc) + timedelta(seconds=3600),
    )


@pytest.fixture
def fake_refresh_token_subject_none() -> Token:
    return Token(
        value="fake_refresh_token",
        token_type="Refresh",
        subject=None,
        expires_at=datetime.now(tz=timezone.utc) + timedelta(seconds=3600),
    )


@pytest.fixture
def refresh_tokens_file_content(
    fake_refresh_token, fake_refresh_token_subject_none
):
    return {
        "fake_refresh_token": fake_refresh_token.to_dict(),
        "fake_refresh_token_subject_none": fake_refresh_token_subject_none.to_dict(),
    }


@pytest.fixture
def refresh_token_storage_file_path(tmp_path):
    return tmp_path / "refresh_tokens.json"


@pytest.fixture
def refresh_token_storage_file(
    refresh_token_storage_file_path, refresh_tokens_file_content
):
    with open(refresh_token_storage_file_path, "w") as f:
        f.write(json.dumps(refresh_tokens_file_content))
    return refresh_token_storage_file_path


@pytest.fixture
def authentication_service_use_refresh_tokens(
    fake_uow,
    fake_static_user,
    fake_identity_provider,
    refresh_token_storage_file,
) -> AuthenticationService:
    return AuthenticationService(
        identity_provider=fake_identity_provider,
        uow=fake_uow,
        users_repository_name="authentication_service",
        static_user=fake_static_user,
        use_cookies=True,
        use_refresh_tokens=True,
        refresh_token_length=28,
        refresh_token_max_age=3600,
        refresh_token_storage="file",
        refresh_token_storage_file_path=refresh_token_storage_file,
    )


@pytest.fixture
def authentication_service_use_refresh_tokens_memory(
    fake_uow, fake_static_user, fake_identity_provider
) -> AuthenticationService:
    return AuthenticationService(
        identity_provider=fake_identity_provider,
        uow=fake_uow,
        users_repository_name="authentication_service",
        static_user=fake_static_user,
        use_cookies=True,
        use_refresh_tokens=True,
        refresh_identity_on_refresh=False,
        refresh_token_storage="memory",
    )


@pytest.fixture
def authentication_service_use_refresh_tokens_memory_expired(
    fake_uow, fake_static_user, fake_identity_provider
) -> AuthenticationService:
    return AuthenticationService(
        identity_provider=fake_identity_provider,
        uow=fake_uow,
        users_repository_name="authentication_service",
        static_user=fake_static_user,
        use_cookies=True,
        use_refresh_tokens=True,
        refresh_token_max_age=-1,
        refresh_identity_on_refresh=False,
        refresh_token_storage="memory",
    )


@pytest.fixture
def authentication_service_use_refresh_tokens_database(
    fake_uow, fake_static_user, fake_identity_provider
) -> AuthenticationService:
    return AuthenticationService(
        identity_provider=fake_identity_provider,
        uow=fake_uow,
        users_repository_name="authentication_service",
        static_user=fake_static_user,
        use_cookies=True,
        use_refresh_tokens=True,
        refresh_identity_on_refresh=False,
        refresh_token_storage="database",
    )
