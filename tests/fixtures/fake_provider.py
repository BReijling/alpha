from alpha.interfaces.token_factory import TokenFactory
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token


class FakeIdentityProvider:
    protocol = "fake_provider"

    def __init__(
        self,
        identity: Identity | None = None,
        token_factory: TokenFactory | None = None,
    ) -> None:
        if identity is None:
            identity = Identity.from_dict({"subject": "fake_subject"})
        self._identity = identity
        self._new_password = None
        self.token_factory = token_factory

    def authenticate(self, *args, **kwargs) -> Identity:
        return self._identity

    def get_user(self, subject: str) -> Identity | None:
        if subject == self._identity.subject:
            return self._identity
        return None

    def issue_token(self, identity: Identity) -> Token:
        return Token("static_user_token")

    def change_password(self, credentials, new_password):
        self._new_password = new_password

    def validate(self, token: Token) -> Identity:
        return self._identity
