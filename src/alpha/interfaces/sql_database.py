from typing import Protocol, runtime_checkable, ClassVar

import sqlalchemy as sa
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session

from alpha.interfaces.sql_mapper import SqlMapper


@runtime_checkable
class SqlDatabase(Protocol):
    _host: ClassVar[str]
    _port: ClassVar[int]
    _username: ClassVar[str]
    _password: ClassVar[str]
    _db_name: ClassVar[str]
    _db_type: ClassVar[str]
    _schema_name: ClassVar[str]
    _mapper: ClassVar[SqlMapper | None]
    _connection_string: ClassVar[str]
    _engine: ClassVar[Engine]
    _session_factory: ClassVar[Session]

    def get_session(self) -> Session: ...

    def engine(self) -> Engine: ...

    def create_tables(
        self, metadata: sa.MetaData, tables: list[sa.Table] | None = None
    ) -> None: ...

    def drop_tables(
        self, metadata: sa.MetaData, tables: list[sa.Table] | None = None
    ) -> None: ...

    def _create_schema(self, engine: Engine, schema_name: str) -> None: ...
