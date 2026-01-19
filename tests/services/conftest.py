import pytest

from alpha.domain.models.user import User
from alpha.services.authentication_service import AuthenticationService


class FakeUserRepository:
    def get_by_id(self, value, attr):
        return User(
            id=1,
            username="testuser",
            email="testuser@example.com",
            role="TESTER",
            groups=["group1", "group2", "group3", "group4"],
            permissions=["read", "write", "modify", "delete"],
            admin=True,
        )


class FakeUnitOfWork:
    def __init__(self):
        self.users = FakeUserRepository()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def commit(self):
        pass


@pytest.fixture
def fake_uow():
    return FakeUnitOfWork()


@pytest.fixture
def authentication_service(fake_uow) -> AuthenticationService:
    return AuthenticationService(identity_provider=None, uow=fake_uow)
