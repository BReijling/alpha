from typing import Any, Sequence

from alpha import exceptions
from alpha.interfaces.token_factory import TokenFactory
from alpha.factories.password_factory import PasswordFactory
from alpha.mixins.jwt_provider import JWTProviderMixin
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity
from alpha.domain.models.user import User


class StaticConfigProvider(JWTProviderMixin):
    """Provides an Identity Provider based on static configuration.

    This provider uses static configuration to supply identity information,
    rather than dynamically querying an external source. The configuration is
    expected to be provided at initialization.

    The password values for each static user need to be hashed before being
    provided to the constructor of this provider. The `hash_password` method of
    the `PasswordFactory` class can be used to hash the passwords before
    providing them. This ensures that the passwords are securely stored and can
    can be verified during authentication. When you use a non-default password
    factory, make sure it is compatible with the hashing and verification
    mechanisms expected by this provider.

    You can use this example with the following command to hash a password:
    ```
    python -c 'from getpass import getpass; from alpha import PasswordFactory;
    print(PasswordFactory().hash_password(getpass("Enter password: ")))'
    ```
    """

    protocol = "static"
    token_factory: TokenFactory | None = None
    _identity_model: type[Identity] = Identity

    def __init__(
        self,
        static_users: Sequence[dict[str, Any]],
        token_factory: TokenFactory | None = None,
        password_factory: PasswordFactory | None = None,
        identity_model: type[Identity] = Identity,
    ):
        """Initialize the static provider with the given configuration.

        Parameters
        ----------
        static_users
            Collection of static user objects to be used by the provider. The
            password values for these users need to be hashed before being
            provided.
        token_factory
            An optional token factory for generating tokens, by default None.
        password_factory
            An optional password factory for handling password operations, by
            default None. If the password factory is not provided, a default
            instance will be used.
        identity_model
            The identity model class to use, by default Identity.
        """
        self._static_users_store = self._build_user_store(static_users)

        self.token_factory = token_factory
        self._password_factory = password_factory or PasswordFactory()
        self._identity_model = identity_model

    def authenticate(
        self,
        credentials: PasswordCredentials,
    ) -> Identity:
        """Authenticate a user based on the provided credentials.

        Parameters
        ----------
        credentials : PasswordCredentials
            The credentials to authenticate the user with.

        Returns
        -------
        Identity
            The authenticated user's identity.

        Raises
        ------
        exceptions.InvalidCredentialsException
            If the provided credentials are invalid.
        """
        user = self._verify_password(credentials)

        return self._identity_model.from_user(user)

    def get_user(
        self,
        subject: str,
    ) -> Identity:
        """Retrieve a user based on the provided subject identifier.

        Parameters
        ----------
        subject : str
            The subject identifier of the user to retrieve.

        Returns
        -------
        Identity
            The identity of the user corresponding to the provided subject.

        Raises
        ------
        exceptions.NotFoundException
            If no user with the provided subject exists.
        """
        user = self._get_user_by_id(subject)

        return self._identity_model.from_user(user)

    def change_password(
        self,
        credentials: PasswordCredentials,
        new_password: str,
    ) -> None:
        """This method is not supported for this identity provider."""
        raise exceptions.NotSupportedException(
            "Static provider does not support changing passwords."
        )

    def _get_user_by_username(
        self,
        username: str,
    ) -> User:
        """Get a user from the store by their username.

        Parameters
        ----------
        username
            The username of the user to retrieve.

        Returns
        -------
            The user corresponding to the provided username.

        Raises
        ------
        exceptions.NotFoundException
            If no user with the provided username exists.
        """
        user = self._static_users_store.get(username)
        if not user:
            raise exceptions.InvalidCredentialsException(
                "Invalid username or password"
            )

        return user

    def _get_user_by_id(
        self,
        user_id: str,
    ) -> User:
        """Get a user from the store by their ID.

        Parameters
        ----------
        user_id
            The ID of the user to retrieve.

        Returns
        -------
        User
            The user corresponding to the provided ID.

        Raises
        ------
        exceptions.NotFoundException
            If no user with the provided ID exists.
        """
        for user in self._static_users_store.values():
            if (str(user.id) if user.id else user.username) == user_id:
                return user

        raise exceptions.InvalidCredentialsException(
            "Invalid username or password"
        )

    def _build_user_store(
        self,
        static_users: Sequence[dict[str, Any]],
    ) -> dict[str, User]:
        """Build a dictionary mapping usernames to User objects from the
        provided static users. The resulting dictionary will have usernames as
        keys and User objects as values. The function also ensures that each
        User has a unique ID.

        Parameters
        ----------
        static_users
            The list of static users to build the store from.

        Returns
        -------
        dict[str, User]
            A dictionary mapping usernames to User objects.
        """
        store: dict[str, User] = {}
        for user_object in static_users:
            user = User.from_dict(user_object)
            username = user.username
            if not username:
                continue
            store[username] = user

        # Check if every User has a unique ID
        user_ids: set[str] = set()
        for user in store.values():
            user_id = str(user.id)
            if user_id in user_ids:
                raise ValueError(
                    f"Duplicate user ID found: {user.id}. Each user must have "
                    "a unique ID."
                )
            user_ids.add(user_id)

        return store

    def _verify_password(self, credentials: PasswordCredentials) -> User:
        """Verify the provided password credentials against the static user store.

        Parameters
        ----------
        credentials
            The credentials to verify.

        Returns
        -------
        User
            The user corresponding to the provided credentials.

        Raises
        ------
        exceptions.InvalidCredentialsException
            If the provided credentials are invalid.
        """
        user = self._get_user_by_username(credentials.username)
        if not self._password_factory.verify_password(
            credentials.password, user.password
        ):
            raise exceptions.InvalidCredentialsException(
                "Invalid username or password"
            )

        return user
