from typing import Any


class FakeSqlAlchemySession:
    def __init__(self, obj: Any = None, *args, **kwargs):
        self.objs = [obj] if obj else []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def query(self, *args, **kwargs):
        return self

    def filter_by(self, *args, **kwargs):
        return self

    def one_or_none(self):
        return self.objs[0] if self.objs else None

    def all(self):
        return self.objs

    def add(self, instance: Any):
        self.objs.append(instance)
        return instance

    def commit(self):
        pass

    def refresh(self, instance: Any):
        return instance

    def delete(self, instance: Any):
        self.objs = self.objs[:-1]
