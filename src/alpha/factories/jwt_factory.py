from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from alpha import exceptions
from alpha.encoder import JSONEncoder


class JWTFactory:
    """An implementation of the TokenFactory interface which can be used to
    generate and decode a JSON Web Token.
    """

    def __init__(
        self,
        secret: str,
        lifetime_hours: str | None = "12",
        issuer: str = "http://localhost",
        jwt_algorithm: str = "HS256",
    ) -> None:
        if not secret:
            raise ValueError("Secret value cannot be empty")
        if lifetime_hours is None:
            lifetime_hours = "12"

        self.JWT_SECRET: str = secret
        self.JWT_ISSUER = issuer
        self.JWT_ALGORITHM = jwt_algorithm
        self.JWT_LIFETIME_SECONDS = 3600 * int(lifetime_hours)

    def create(
        self,
        subject: str,
        payload: dict[str, Any],
        not_before: datetime | None = None,
    ) -> str:
        """Create a JWT token for a subject.

        Parameters
        ----------
        subject
            The unique identifier for the subject.
        payload
            A dictionary containing payload data, such as an object containing
            user information.
        not_before
            An optional datetime indicating when the token becomes valid.

        Returns
        -------
            The generated JWT token as a string.
        """
        now = datetime.now(tz=timezone.utc)
        exp = now + timedelta(seconds=self.JWT_LIFETIME_SECONDS)

        token_payload: dict[str, Any] = {
            "sub": subject,
            "iat": int(now.timestamp()),
            "nbf": (
                int(not_before.timestamp())
                if not_before
                else int(now.timestamp())
            ),
            "exp": int(exp.timestamp()),
            "iss": self.JWT_ISSUER,
            "payload": payload,
        }

        token = jwt.encode(
            payload=token_payload,
            key=self.JWT_SECRET,
            algorithm=self.JWT_ALGORITHM,
            json_encoder=JSONEncoder,
        )
        return token

    def validate(self, token: str) -> bool:
        """Validate a JWT token.

        Parameters
        ----------
        token
            The JWT token to be validated.

        Returns
        -------
            True if the token is valid, False otherwise.

        Raises
        ------
            TokenExpiredException
                If the token has expired.
            InvalidSignatureException
                If the token signature is invalid.
        """
        try:
            jwt.decode(
                jwt=token,
                key=self.JWT_SECRET,
                algorithms=[self.JWT_ALGORITHM],
                issuer=self.JWT_ISSUER,
                verify=True,
            )
            return True
        except jwt.ExpiredSignatureError as e:
            raise exceptions.TokenExpiredException(str(e)) from e
        except jwt.InvalidSignatureError as e:
            raise exceptions.InvalidSignatureException(str(e)) from e
        except jwt.PyJWTError as e:
            raise exceptions.InvalidTokenException(
                f"Token is invalid: {str(e)}"
            ) from e

    def get_payload(self, token: str) -> dict[str, Any]:
        """Retrieve the payload from a JWT token.

        Parameters
        ----------
        token
            The JWT token from which to extract the payload.

        Returns
        -------
            A dictionary containing the payload data extracted from the token.
        """
        decoded: dict[str, Any] = jwt.decode(
            jwt=token,
            key=self.JWT_SECRET,
            algorithms=[self.JWT_ALGORITHM],
            issuer=self.JWT_ISSUER,
        )
        return decoded.get("payload", {})
