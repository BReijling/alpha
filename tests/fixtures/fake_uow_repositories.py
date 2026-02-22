from alpha.domain.models.user import User
from alpha.factories.password_factory import PasswordFactory


class FakeAuthenticationServiceUserRepository:
    def get_by_id(self, *args, **kwargs) -> User:
        return User(
            id=1,
            username="testuser",
            email="testuser@example.com",
            role="TESTER",
            groups=["group1", "group2", "group3", "group4"],
            permissions=["read", "write", "modify", "delete"],
            admin=True,
        )


class FakeDatabaseProviderUserRepository:
    def get_one_or_none(self, *args, **kwargs) -> User:
        return User(
            id=1,
            username="test_user",
            password=PasswordFactory().hash_password("test_password"),
            email="test_user@example.com",
        )


class FakeDatabaseProviderUserRepositoryEmptyPassword:
    def get_one_or_none(self, *args, **kwargs) -> User:
        return User(
            id=1,
            username="test_user",
            password=None,
            email="test_user@example.com",
        )


class FakeDatabaseProviderUserRepositoryNoUser:
    def get_one_or_none(self, *args, **kwargs) -> None:
        return None


class FakeUnitOfWork:
    def __init__(self):
        self.authentication_service = FakeAuthenticationServiceUserRepository()
        self.database_provider = FakeDatabaseProviderUserRepository()
        self.database_provider_empty_password = (
            FakeDatabaseProviderUserRepositoryEmptyPassword()
        )
        self.database_provider_no_user = (
            FakeDatabaseProviderUserRepositoryNoUser()
        )

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def commit(self):
        pass
