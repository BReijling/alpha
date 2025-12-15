"""Contains KaartenbakTokenFactory class"""

import time
from typing import Any
from uuid import UUID

import jwt

from alpha.exceptions import UnauthorizedException
from alpha.encoder import JSONEncoder

from alpha import exceptions


class TokenFactory:
    """An implementation of the TokenFactory interface which can be used to
    generate and decode a JSON Web Token.
    """

    def __init__(
        self,
        secret: str | None,
        lifetime_hours: int = 12,
        issuer: str = "http://localhost",
    ) -> None:
        if secret is None:
            raise ValueError("Secret value cannot be None")

        self.JWT_ISSUER = issuer
        self.JWT_SECRET = secret
        self.JWT_LIFETIME_SECONDS = 3600 * lifetime_hours
        self.JWT_ALGORITHM = "HS256"

    def generate_token(
        self, data: dict[str, Any], user_id: UUID | str | None = None
    ) -> str:
        """Generate a JSON Web Token

        Parameters
        ----------
        user
            User object

        Returns
        -------
            A JSON Web Token
        """
        timestamp = self._current_timestamp()
        payload: dict[str, Any] = {
            "iss": self.JWT_ISSUER,
            "iat": int(timestamp),
            "exp": int(timestamp + self.JWT_LIFETIME_SECONDS),
            "data": data,
            "sub": str(user_id),
        }

        return jwt.encode(
            payload,
            self.JWT_SECRET,
            algorithm=self.JWT_ALGORITHM,
            json_encoder=JSONEncoder,
        )

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode a JSON Web Token

        Parameters
        ----------
        token
            A JSON Web Token

        Returns
        -------
            Object of the decoded JSON Web Token

        Raises
        ------
        UnauthorizedException
            In case of an invalid JSON Web Token
        """
        try:
            return jwt.decode(
                jwt=token,
                key=self.JWT_SECRET,
                algorithms=[self.JWT_ALGORITHM],
                verify=True,
            )
        except jwt.DecodeError as e:
            raise exceptions.InvalidTokenException(e)
        except jwt.ExpiredSignatureError as e:
            raise exceptions.InvalidTokenException(e)

    def get_user_from_token(self, token: str) -> User:
        """Get the User object from a JSON Web Token

        Parameters
        ----------
        token
            A JSON Web Token

        Returns
        -------
            User object

        Raises
        ------
        UnauthorizedException
            In case of an invalid JSON Web Token or if the user ID is missing
            or invalid in the token payload
        """
        decoded_token = self.decode_token(token)

        user_data = decoded_token.get("user", None)
        if not user_data:
            raise UnauthorizedException("User data is missing in token")

        return User.from_token_user_data(user_data)

    def _current_timestamp(self) -> int:
        """Get the current timestamp

        Returns
        -------
            Current timestamp value
        """
        return int(time.time())
