from datetime import datetime, timedelta, timezone
from typing import Any
import warnings

import jwt

from alpha import exceptions
from alpha.encoder import JSONEncoder


class JWTFactory:
    """An implementation of the TokenFactory interface which can be used to
    generate and decode a JSON Web Token. The `pyjwt` library is used to handle
    the encoding and decoding of the JWT. The JWTFactory class provides methods
    for creating a JWT token, validating a JWT token, and retrieving the
    payload from a JWT token. The class is initialized with a secret key,
    token lifetime, issuer, algorithm, and decoding options.
    """

    def __init__(
        self,
        secret: str,
        lifetime_hours: int | None = None,
        lifetime_seconds: int | None = None,
        issuer: str = "http://localhost",
        jwt_algorithm: str = "HS256",
        options: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the JWTFactory. This method sets up the necessary
        configuration for creating and validating JWT tokens. It requires a
        secret key for signing the tokens and allows optional configuration
        for token lifetime, issuer, algorithm, and decoding options.

        Parameters
        ----------
        secret
            The secret key used to sign the JWT.
        lifetime_hours
            The lifetime of the JWT in hours, by default None. This parameter
            is ignored if lifetime_seconds is provided. The parameter is
            deprecated in favor of lifetime_seconds and will be removed in a
            future release.
        lifetime_seconds
            The lifetime of the JWT in seconds, by default None. If both
            lifetime_hours and lifetime_seconds are provided, lifetime_seconds
            will take precedence. If neither is provided, the default lifetime
            will be 900 seconds (15 minutes).
        issuer
            The issuer of the JWT, by default "http://localhost"
        jwt_algorithm
            The algorithm used to sign the JWT, by default "HS256"
        options
            A dictionary of options to customize the decoding behavior, by
            default None. If not provided, it defaults to requiring all
            standard claims (exp, iat, nbf, iss, sub) and verifying the
            signature.

        Raises
        ------
        ValueError
            If the secret value is empty.
        """
        if not secret:
            raise ValueError("Secret value cannot be empty")

        if lifetime_hours:
            warnings.warn(
                "The lifetime_hours parameter is deprecated and will be "
                "removed in a future release.",
                DeprecationWarning,
                stacklevel=2,
            )

        if lifetime_seconds is None and lifetime_hours is not None:
            lifetime_seconds = 3600 * int(lifetime_hours)

        lifetime_seconds = (
            900 if lifetime_seconds is None else lifetime_seconds
        )  # Default to 15 minutes if no lifetime is provided

        self.JWT_SECRET: str = secret
        self.JWT_ISSUER = issuer
        self.JWT_ALGORITHM = jwt_algorithm
        self.JWT_LIFETIME_SECONDS = lifetime_seconds
        self.JWT_OPTIONS = options or {
            "require": ["exp", "iat", "nbf", "iss", "sub"],
            "verify_signature": True,
        }

    def create(
        self,
        subject: str,
        payload: dict[str, Any],
        not_before: datetime | None = None,
    ) -> str:
        """Creates a JWT token for a given subject and payload, with an
        optional `not_before` parameter to specify when the token becomes
        valid.

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
        str
            The generated JWT token as a string.
        """
        now = datetime.now(tz=timezone.utc)
        exp = now + timedelta(seconds=float(self.JWT_LIFETIME_SECONDS))

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

    def validate(
        self, token: str, options: dict[str, Any] | None = None
    ) -> bool:
        """Validate a JWT token. This method checks the token's signature,
        expiration, and issuer. If the token is invalid, it raises an
        appropriate exception. If the token is valid, it returns True.

        If the `options` parameter is provided, it will be passed to the
        `jwt.decode` function. This allows customization of the decoding
        behavior, such as enabling or disabling signature verification.

        Parameters
        ----------
        token
            The JWT token to be validated.
        options
            A dictionary of options to customize the decoding behavior.

        Returns
        -------
        bool
            True if the token is valid, False otherwise.

        Raises
        ------
            TokenExpiredException
                If the token has expired.
            InvalidSignatureException
                If the token signature is invalid.
        """
        if self._decode(token, options):
            return True
        return False

    def get_payload(
        self, token: str, options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Retrieve the payload from a JWT token. This method decodes the token
        and extracts the payload data. If the token is invalid, it raises an
        appropriate exception. If the token is valid, it returns the payload.

        If the `options` parameter is provided, it will be passed to the
        `jwt.decode` function. This allows customization of the decoding
        behavior, such as enabling or disabling signature verification.

        Parameters
        ----------
        token
            The JWT token from which to extract the payload.
        options
            A dictionary of options to customize the decoding behavior.

        Returns
        -------
        dict[str, Any]
            A dictionary containing the payload data extracted from the token.
        """
        decoded = self._decode(token, options)
        return decoded.get("payload", {})

    def _decode(
        self, token: str, options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Decode a JWT token without performing validation. This method is
        intended for internal use and should not be exposed as part of the
        public API.

        Parameters
        ----------
        token
            The JWT token to be decoded.
        options
            A dictionary of options to customize the decoding behavior.

        Returns
        -------
        dict[str, Any]
            A dictionary containing the decoded token data.
        """
        try:
            decoded: dict[str, Any] = jwt.decode(
                jwt=token,
                key=self.JWT_SECRET,
                algorithms=[self.JWT_ALGORITHM],
                issuer=self.JWT_ISSUER,
                options=options or self.JWT_OPTIONS,
            )
            return decoded
        except jwt.ExpiredSignatureError as e:
            raise exceptions.TokenExpiredException(str(e)) from e
        except jwt.InvalidSignatureError as e:
            raise exceptions.InvalidSignatureException(str(e)) from e
        except jwt.PyJWTError as e:
            raise exceptions.InvalidTokenException(
                f"Token is invalid: {str(e)}"
            ) from e
