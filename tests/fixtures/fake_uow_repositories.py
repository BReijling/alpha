from alpha.domain.models.user import User


class FakeRepository:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def add(self, *args, **kwargs) -> None:
        pass

    def add_all(self, *args, **kwargs) -> None:
        pass

    def get(self, *args, **kwargs) -> None:
        pass

    def get_all(self, *args, **kwargs) -> None:
        pass

    def patch(self, *args, **kwargs) -> None:
        pass

    def remove(self, *args, **kwargs) -> None:
        pass

    def update(self, *args, **kwargs) -> None:
        pass


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
    def __init__(self, users: list[User] | None = None):
        self.users = users

    def get_by_id(self, *args, **kwargs) -> User:
        return self.users[0]

    def get_one_or_none(self, *args, **kwargs) -> User:
        return self.users[0]


class FakeDatabaseProviderUserRepositoryNoUser:
    def get_one_or_none(self, *args, **kwargs) -> None:
        return None


class FakeUnitOfWork:
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def commit(self):
        pass
