from lib.identity_provider import IdentityProvider
from alpha.interfaces.token_factory import TokenFactory
from alpha import exceptions


class AuthenticationService:
    def __init__(
        self,
        token_factory: TokenFactory,
        identity_provider: IdentityProvider,
        user_id_attribute: str = "user_id",
    ) -> None:
        self.token_factory = token_factory
        self.identity_provider = identity_provider
        self.user_id_attribute = user_id_attribute

    def login(self, username: str, password: str) -> str:
        user = self.identity_provider.authenticate(username, password)
        if not user:
            raise exceptions.UnauthorizedException("Invalid credentials")

        user_id = getattr(user, self.user_id_attribute, None)
        if not user_id:
            raise exceptions.InternalServerErrorException(
                "User ID attribute missing"
            )

        return self.token_factory.create(user.id, user.to_dict())

    def logout(self, token: str) -> str:
        if not self.token_factory.validate(token):
            raise exceptions.UnauthorizedException("Invalid token")

        return "Logged out"

    def get_user_info(self, token: str) -> dict[str, str]:
        if not self.token_factory.validate(token):
            raise exceptions.UnauthorizedException("Invalid token")

        payload = self.token_factory.get_payload(token)
        return payload

    def refresh_token(self, token: str) -> str:
        if not self.token_factory.validate(token):
            raise exceptions.UnauthorizedException("Invalid token")

        payload = self.token_factory.get_payload(token)
        user_id = payload.get(self.user_id_attribute)
        if not user_id:
            raise exceptions.BadRequestException("Invalid token payload")

        return self.token_factory.create(user_id, payload)

    def change_password(
        self,
        username: str,
        password: str,
        new_password: str,
    ) -> bool:
        user = self.identity_provider.authenticate(username, password)
        if not user:
            raise exceptions.UnauthorizedException("Invalid credentials")

        return self.identity_provider.change_password(username, new_password)

    def pretend_login(self, user_id: str) -> str:
        user_info = self.identity_provider.get_user_info(user_id)
        if not user_info:
            raise exceptions.NotFoundException("User not found")

        return self.token_factory.create(user_id, user_info)
