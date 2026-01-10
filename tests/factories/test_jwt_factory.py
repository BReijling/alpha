import pytest
from datetime import datetime
from alpha import exceptions
from alpha.factories.jwt_factory import JWTFactory
from alpha.interfaces.token_factory import TokenFactory


def test_jwt_factory_init():
    jwt_factory = JWTFactory(secret="mysecret")
    assert isinstance(jwt_factory, TokenFactory)

    with pytest.raises(ValueError) as exc_info:
        JWTFactory(secret="")
        assert str(exc_info.value) == ("Secret value cannot be empty")


def test_jwt_factory_create_token(
    jwt_factory_factory, jwt_secret, jwt_issuer, jwt_lifetime_hours
):
    jwt_factory: JWTFactory = jwt_factory_factory(
        jwt_secret, jwt_issuer, jwt_lifetime_hours
    )
    token = jwt_factory.create(
        subject="test_subject", payload={"key": "value"}
    )
    assert isinstance(token, str)
    assert len(token.split(".")) == 3


def test_jwt_factory_validate_token(jwt_factory: JWTFactory):
    token = jwt_factory.create(
        subject="test_subject", payload={"key": "value"}
    )
    assert jwt_factory.validate(token)


def test_jwt_factory_validate_invalid_token(
    jwt_factory_factory,
    jwt_secret,
    jwt_factory,
    jwt_issuer,
    jwt_lifetime_hours,
):
    # test invalid signature
    other_jwt_factory: JWTFactory = jwt_factory_factory(
        "anothersecretkey", jwt_issuer, jwt_lifetime_hours
    )

    invalid_secret_token = other_jwt_factory.create(
        subject="test_subject", payload={"key": "value"}
    )

    with pytest.raises(exceptions.InvalidSignatureException):
        jwt_factory.validate(invalid_secret_token)

    # test expired token
    other_jwt_factory: JWTFactory = jwt_factory_factory(
        jwt_secret, jwt_issuer, 0
    )

    invalid_secret_token = other_jwt_factory.create(
        subject="test_subject", payload={"key": "value"}
    )

    with pytest.raises(exceptions.TokenExpiredException):
        jwt_factory.validate(invalid_secret_token)

    # test not before in the future
    invalid_secret_token = jwt_factory.create(
        subject="test_subject",
        payload={"key": "value"},
        not_before=datetime(3000, 1, 1),
    )

    with pytest.raises(exceptions.InvalidTokenException):
        jwt_factory.validate(invalid_secret_token)


def test_jwt_factory_get_payload(jwt_factory: JWTFactory, jwt_payload):
    token = jwt_factory.create(subject="test_subject", payload=jwt_payload)

    payload = jwt_factory.get_payload(token)
    assert payload["sub"] == "user123"
    assert payload == jwt_payload
