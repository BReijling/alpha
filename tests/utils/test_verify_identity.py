import pytest

from alpha.exceptions import InsufficientPermissionsException
from alpha.utils.verify_identity import verify_identity


def test_verify_identity(identity):
    verify_identity(
        identity=identity,
        roles=None,
        groups=None,
        permissions=None,
    )

    verify_identity(
        identity=identity,
        roles=[],
        groups=[],
        permissions=[],
    )

    verify_identity(
        identity=identity,
        roles=["SUPERUSER"],
        groups=None,
        permissions=None,
    )

    verify_identity(
        identity=identity.to_dict(),
        roles=["SUPERUSER", "ADMIN"],
        groups=["group1", "group3"],
        permissions=["read", "write"],
    )

    with pytest.raises(InsufficientPermissionsException):
        verify_identity(
            identity=identity,
            roles=["ADMIN"],
            groups=None,
            permissions=None,
        )

    with pytest.raises(InsufficientPermissionsException):
        verify_identity(
            identity=identity,
            roles=None,
            groups=["group3", "group4"],
            permissions=None,
        )

    with pytest.raises(InsufficientPermissionsException):
        verify_identity(
            identity=identity,
            roles=None,
            groups=None,
            permissions=["read", "delete"],
        )
