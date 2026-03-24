from typing import Any


class FakeSqlAlchemySession:
    def __init__(self, obj: Any = None, *args, **kwargs):
        self.obj = obj

    def query(self, *args, **kwargs):
        return self.obj

    def add(self, instance: Any):
        return instance

    def commit(self):
        pass

    def delete(self, instance: Any):
        return instance
