from typing import Any

from tests.fixtures.fake_session import FakeSqlAlchemySession


class FakeSqlAlchemyConnector:
    def __init__(self, obj: Any, *args, **kwargs):
        self.session = FakeSqlAlchemySession(obj=obj)

    def get_session(self):
        return self.session
