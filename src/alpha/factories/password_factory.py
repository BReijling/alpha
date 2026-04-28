"""Contains PasswordFactory class with password hashing methods
hash_password & verify_password
"""

import argon2
from argon2.exceptions import VerifyMismatchError

from alpha import exceptions


class PasswordFactory:
    """This class provides methods for hashing and verifying passwords using
    the argon2 library.
    """

    def __init__(
        self, password_hasher: argon2.PasswordHasher | None = None
    ) -> None:
        """Initialize the PasswordFactory.

        Parameters
        ----------
        password_hasher
            An optional password hasher instance. If not provided, a default
            argon2.PasswordHasher with a salt length of 16 will be used.
        """
        self._password_hasher = password_hasher or argon2.PasswordHasher(
            salt_len=16
        )

    def hash_password(
        self, password: str | None, convert_to_hex: bool = True
    ) -> str:
        """Hashes the provided password using the password hasher.

        By default the hashed password is converted to hexadecimal format for
        storage. This ensures that the hashed password can be safely stored in
        a database or other storage medium. If you prefer to store the hashed
        password in its original format, you can set the `convert_to_hex`
        parameter to False.

        Parameters
        ----------
        password
            The password to be hashed.
        convert_to_hex
            A boolean flag indicating whether to convert the hashed password to
            hexadecimal format. Defaults to True.

        Returns
        -------
        str
            The hashed password as a hexadecimal string.

        Raises
        ------
        exceptions.WrongPasswordException
            Raised when the provided password is None or empty.
        """
        if not password:
            raise exceptions.WrongPasswordException("Password value is empty")
        hashed_password = self._password_hasher.hash(password=password)
        return (
            self._to_hex(hashed_password)
            if convert_to_hex
            else hashed_password
        )

    def verify_password(
        self,
        password: str | None,
        hash: str | None,
        convert_from_hex: bool = True,
    ) -> bool:
        """Verifies the provided password against the given hash using the
        password hasher.

        By default, it is assumed that the provided hash is in hexadecimal
        format. If the hash is in its original format, you can set the
        `convert_from_hex` parameter to False to skip the conversion step.

        Parameters
        ----------
        password
            The password to be verified.
        hash
            The hash to verify the password against.
        convert_from_hex
            A boolean flag indicating whether to convert the hash from
            hexadecimal format before verification. Defaults to True.

        Returns
        -------
        bool
            True if the password matches the hash, False otherwise.

        Raises
        ------
        exceptions.WrongPasswordException
            Raised when the provided password is None or empty.
        exceptions.MissingPasswordException
            Raised when the provided hash is None or empty.
        """
        if not password:
            raise exceptions.WrongPasswordException("Password value is empty")
        if not hash:
            raise exceptions.MissingPasswordException(
                "No password value to compare with"
            )

        try:
            return self._password_hasher.verify(
                hash=self._from_hex(hash) if convert_from_hex else hash,
                password=password,
            )
        except VerifyMismatchError:
            return False

    def _to_hex(self, value: str) -> str:
        """Converts a string value to its hexadecimal representation.

        Parameters
        ----------
        value
            The string value to be converted to hexadecimal.

        Returns
        -------
        str
            The hexadecimal representation of the string value.
        """
        return value.encode("utf-8").hex()

    def _from_hex(self, hex: str) -> str:
        """Converts a hexadecimal string back to its original string
        representation.

        Parameters
        ----------
        hex
            The hexadecimal string to be converted back to the original string.

        Returns
        -------
        str
            The original string representation of the hexadecimal input.
        """
        return bytes.fromhex(hex).decode("utf-8")
