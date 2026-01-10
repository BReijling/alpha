import pytest

from alpha.exceptions import MissingDependencyException
from alpha.mixins.jwt_provider import JWTProviderMixin
from alpha.providers.models.token import Token


def test_jwt_provider_initialize():
    jwt_provider = JWTProviderMixin()

    with pytest.raises(MissingDependencyException):
        jwt_provider.validate("dummy_token")
    with pytest.raises(MissingDependencyException):
        jwt_provider.issue_token("dummy_identity")


def test_jwt_provider_validate(jwt_provider, fake_jwt_factory, jwt_payload):
    token = fake_jwt_factory.create(
        subject=jwt_payload["subject"], payload=jwt_payload
    )
    print(f"{token=}")
    identity = jwt_provider.validate(Token(token, token_type="Bearer"))

    assert identity.subject == jwt_payload["subject"]
    assert identity.username == jwt_payload["username"]
    assert identity.email == jwt_payload["email"]

    fake_jwt_factory._payload = {}  # Simulate missing subject
    incomplete_token = fake_jwt_factory.create(
        subject=jwt_payload["subject"], payload={}  # Missing subject
    )

    print(f"{incomplete_token=}")
    with pytest.raises(ValueError):
        jwt_provider.validate(Token(incomplete_token, token_type="Bearer"))


def test_jwt_provider_issue_token(jwt_provider, identity):
    token = jwt_provider.issue_token(identity)

    assert token.token_type == "Bearer"
    assert token.value == "token_for_testuser"
