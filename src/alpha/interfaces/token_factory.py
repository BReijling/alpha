from typing import Protocol


class TokenFactory(Protocol):
    """Token Factory interface for creating and validating authentication
    tokens.
    """

    def create(self, user_id: str, payload: dict[str, str]) -> str:
        """Create an authentication token for a user.

        Parameters
        ----------
        user_id
            The unique identifier for the user.
        payload
            A dictionary containing payload data, such as an object containing
            user information.

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
