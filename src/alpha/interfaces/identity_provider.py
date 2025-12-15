from typing import Protocol


class IdentityProvider(Protocol):
    """Identity Provider interface for user authentication and information
    retrieval.
    """

    def authenticate(self, credentials: dict[str, str]) -> bool:
        """Authenticate a user based on provided credentials.

        Parameters
        ----------
        credentials
            The user's credentials, typically including a username and
            password.

        Returns
        -------
            bool
                True if authentication is successful, False otherwise.
        """
        ...

    def get_user_info(self, user_id: str) -> dict[str, str]:
        """Retrieve user information based on user ID.

        Parameters
        ----------
        user_id
            The unique identifier for the user.

        Returns
        -------
            dict[str, str]
                A dictionary containing user information, such as username and
                email.
        """
        ...

    def change_password(self, user_id: str, new_password: str) -> bool:
        """Change the password for a user.

        Parameters
        ----------
        user_id
            The unique identifier for the user.
        new_password
            The new password to be set for the user.

        Returns
        -------
            bool
                True if the password change is successful, False otherwise.
        """
        ...
