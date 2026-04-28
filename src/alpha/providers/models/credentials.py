from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordCredentials:
    """Represents a set of credentials consisting of a username and password.

    Attributes
    ----------
    username
        The username associated with the credentials.
    password
        The password associated with the credentials.
    """

    username: str
    password: str

    def to_dict(self) -> dict[str, str]:
        """Converts the PasswordCredentials instance to a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary representation of the PasswordCredentials instance
            with the following keys:

            - "username": The username associated with the credentials.
            - "password": The password associated with the credentials.
        """
        return {"username": self.username, "password": self.password}

    def __str__(self) -> str:
        """Returns the string representation of the PasswordCredentials
        instance.
        """
        return self.username

    def __repr__(self) -> str:
        """Returns the string representation of the PasswordCredentials
        instance. The password is masked for security reasons.
        """
        return f"PasswordCredentials(username={self.username!r}, password=***)"
