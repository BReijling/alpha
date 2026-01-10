from datetime import datetime
from typing import Any
import pytest

from alpha.mixins.jwt_provider import JWTProviderMixin

from alpha.providers.models.identity import Identity


class FakeJWTFactory:
    def __init__(
        self, jwt_payload: dict[str, Any], validate: bool = True
    ) -> None:
        self._payload = jwt_payload
        self._validate = validate

    def create(
        self,
        subject: str,
        payload: dict[str, Any],
        not_before: datetime | None = None,
    ) -> str:
        # Simulate token creation
        return f"token_for_{subject}"

    def validate(self, token: str) -> bool:
        # Simulate token validation
        return self._validate

    def get_payload(self, token: str) -> dict[str, Any]:
        # Simulate extracting payload from token
        return self._payload


@pytest.fixture
def test_user_id() -> str:
    return "testuser"


@pytest.fixture
def jwt_payload(test_user_id: str) -> dict[str, Any]:
    return {
        "subject": test_user_id,
        "username": "Test User",
        "email": "testuser@example.com",
    }


@pytest.fixture
def fake_jwt_factory(jwt_payload: dict[str, Any]) -> FakeJWTFactory:
    factory = FakeJWTFactory(jwt_payload)
    return factory


@pytest.fixture
def jwt_provider(fake_jwt_factory):
    provider = JWTProviderMixin()
    provider._token_factory = fake_jwt_factory
    return provider


@pytest.fixture
def identity(test_user_id: str):
    return Identity.from_dict(
        {
            "subject": test_user_id,
            "username": "Test User",
            "email": "testuser@example.com",
            "display_name": "Test User",
        }
    )
