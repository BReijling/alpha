from datetime import datetime, timedelta, timezone
from typing import Any

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
    
    The `create` method generates a JWT token for a given subject and payload, 
    with an optional `not_before` parameter to specify when the token becomes 
    valid. 
    
    The `validate` method checks the validity of a JWT token and raises 
    appropriate exceptions if the token is invalid. 
    
    The `get_payload` method retrieves the payload from a JWT token without
    verifying its signature.
    """

    def __init__(
        self,
        secret: str,
        lifetime_hours: str | None = "12",
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
            The lifetime of the JWT in hours, by default "12"
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
        if lifetime_hours is None:
            lifetime_hours = "12"

        self.JWT_SECRET: str = secret
        self.JWT_ISSUER = issuer
        self.JWT_ALGORITHM = jwt_algorithm
        self.JWT_LIFETIME_SECONDS = 3600 * int(lifetime_hours)
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

    def validate(
        self, token: str, options: dict[str, Any] | None = None
    ) -> bool:
        """Validate a JWT token. This method checks the token's signature,
        expiration, and issuer. If the token is invalid, it raises an
        appropriate exception. If the token is valid, it returns True.

        Parameters
        ----------
        token
            The JWT token to be validated.
        options
            A dictionary of options to customize the decoding behavior.

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
