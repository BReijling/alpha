from typing import Any

from alpha.domain.models.group import Group
from alpha.domain.models.user import User
from alpha.providers.models.token import Token


class FakeRepository:
    def __init__(self, objs: list[Any] | None = None, *args, **kwargs) -> None:
        self.objs = objs or []

    def add(self, obj: Any, *args, **kwargs) -> Any:
        self.objs.append(obj)
        return obj

    def add_all(self, *args, **kwargs) -> None:
        self.objs.extend(args[0])

    def get(self, id: Any, *args, **kwargs) -> None:
        return self.objs[0] if self.objs else None

    def get_by_id(self, *args, **kwargs) -> Any:
        return self.objs[0] if self.objs else None

    def get_one_or_none(self, *args, **kwargs) -> User | None:
        return self.objs[0] if self.objs else None

    def get_all(self, *args, **kwargs) -> None:
        return self.objs

    def patch(self, *args, **kwargs) -> None:
        pass

    def remove(self, *args, **kwargs) -> None:
        self.objs = self.objs[1:]

    def select(self, *args, **kwargs) -> None:
        return self.objs

    def update(self, obj: Any, *args, **kwargs) -> None:
        return obj


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


class FakeDatabaseProviderUserRepository(FakeRepository):
    def __init__(self, users: list[User] | None = None):
        self.objs = users or []

    def add(self, user: User, *args, **kwargs) -> User:
        self.objs.append(user)
        return user

    def get_one_or_none(self, *args, **kwargs) -> User | None:
        return self.objs[0] if self.objs else None


class FakeDatabaseProviderGroupRepository(FakeRepository):
    def __init__(self, groups: list[Group] | None = None):
        self.objs = groups or []

    def select(self, *args, **kwargs) -> list[Group] | None:
        return self.objs


class FakeRefreshTokenRepository:
    def __init__(self, tokens: list[Token] | None = None):
        self.tokens = tokens or []

    def add(self, token: Token, *args, **kwargs) -> Token:
        self.tokens.append(token)
        return token

    def get_one_or_none(self, *args, **kwargs) -> Token | None:
        if not self.tokens:
            return None
        return self.tokens[0]


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
