from argon2 import PasswordHasher
import pytest
from alpha import exceptions
from alpha.factories.password_factory import PasswordFactory


def test_password_factory(password_factory: PasswordFactory):
    assert isinstance(password_factory._password_hasher, PasswordHasher)  # type: ignore

    assert PasswordFactory("test")._password_hasher == "test"  # type: ignore

    password = "secret_password"
    hashed_password = password_factory.hash_password(password)
    assert isinstance(hashed_password, str)
    assert hashed_password != password

    # Verify the password
    assert password_factory.verify_password(password, hashed_password) is True
    assert (
        password_factory.verify_password("wrong_password", hashed_password)
        is False
    )

    # Test empty password hashing
    with pytest.raises(exceptions.WrongPasswordException):
        password_factory.hash_password("")

    # Test None password hashing
    with pytest.raises(exceptions.WrongPasswordException):
        password_factory.hash_password(None)

    # Test empty password verification
    with pytest.raises(exceptions.WrongPasswordException):
        password_factory.verify_password("", hashed_password)

    # Test None password verification
    with pytest.raises(exceptions.WrongPasswordException):
        password_factory.verify_password(None, hashed_password)

    # Test empty hash verification
    with pytest.raises(exceptions.MissingPasswordException):
        password_factory.verify_password(password, "")

    # Test None hash verification
    with pytest.raises(exceptions.MissingPasswordException):
        password_factory.verify_password(password, None)
