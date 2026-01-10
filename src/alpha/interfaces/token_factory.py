from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class TokenFactory(Protocol):
    """Token Factory interface for creating and validating authentication
    tokens.
    """

    def create(
        self,
        subject: str,
        payload: dict[str, str],
        not_before: datetime | None = None,
    ) -> str:
        """Create an authentication token for a subject.

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
                The generated authentication token as a string.
        """
        ...

    def validate(self, token: str) -> bool:
        """Validate an authentication token.

        Parameters
        ----------
        token
            The authentication token to be validated.

        Returns
        -------
            bool
                True if the token is valid, False otherwise.
        """
        ...

    def get_payload(self, token: str) -> dict[str, str]:
        """Retrieve the payload from an authentication token.

        Parameters
        ----------
        token
            The authentication token from which to extract the payload.

        Returns
        -------
            dict[str, str]
                A dictionary containing the payload data extracted from the
                token.
        """
        ...
