"""_summary_"""

import sqlalchemy as sa
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.orm.session import Session

from alpha.interfaces.sql_mapper import SqlMapper


class SqlAlchemyDatabase:
    """_summary_"""

    def __init__(
        self,
        host: str = "",
        port: int | None = None,
        username: str = "",
        password: str = "",
        db_name: str = "",
        db_type: str = "postgresql",
        conn_str: str | None = None,
        schema_name: str = "public",
        create_schema: bool = True,
        create_tables: bool = True,
        pool_pre_ping: bool = False,
        mapper: SqlMapper | None = None,
    ) -> None:
        """_summary_

        Parameters
        ----------
        host : str, optional
            _description_, by default ""
        port : int | None, optional
            _description_, by default None
        username : str, optional
            _description_, by default ""
        password : str, optional
            _description_, by default ""
        db_name : str, optional
            _description_, by default ""
        db_type : str, optional
            _description_, by default "postgresql"
        conn_str : str | None, optional
            _description_, by default None
        schema_name : str, optional
            _description_, by default "public"
        create_schema : bool, optional
            _description_, by default True
        create_tables : bool, optional
            _description_, by default True
        mapper : interfaces.SqlMapper | None, optional
            _description_, by default None
        """
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._db_name = db_name
        self._db_type = db_type
        self._schema_name = schema_name
        self._mapper = mapper

        if conn_str is None:
            conn_str = (
                f"{self._db_type}://{self._username}:"
                + f"{self._password}@{self._host}:{self._port}/{self._db_name}"
            )
        self._connection_string = conn_str

        self._engine = sa.create_engine(
            self._connection_string, pool_pre_ping=pool_pre_ping
        )
        self._session_factory = scoped_session(
            sessionmaker(bind=self._engine, autocommit=False, expire_on_commit=False)
        )

        if self._mapper:
            if not self._mapper.started:
                self._mapper.start_mapping()
            if create_tables:
                self.create_tables(self._mapper.metadata)

        if hasattr(self._engine.dialect, "has_schema") & create_schema:
            self._create_schema(self._engine, self._schema_name)

    def get_session(self) -> Session:
        """_summary_

        Returns
        -------
        Session
            _description_
        """
        return self._session_factory()

    def engine(self) -> Engine:
        """_summary_

        Returns
        -------
        Engine
            _description_
        """
        return self._engine

    def create_tables(
        self, metadata: sa.MetaData, tables: list[sa.Table] | None = None
    ) -> None:
        """_summary_

        Parameters
        ----------
        metadata : sa.MetaData
            _description_
        tables : list[sa.Table] | None, optional
            _description_, by default None
        """
        metadata.create_all(self._engine, tables=tables)

    def drop_tables(
        self, metadata: sa.MetaData, tables: list[sa.Table] | None = None
    ) -> None:
        """_summary_

        Parameters
        ----------
        metadata : sa.MetaData
            _description_
        tables : list[sa.Table] | None, optional
            _description_, by default None
        """
        metadata.drop_all(self._engine, tables=tables)

    def _create_schema(self, engine: Engine, schema_name: str) -> None:
        """_summary_

        Parameters
        ----------
        engine : Engine
            _description_
        schema_name : str
            _description_
        """
        major, *_ = sa.__version__.split(".")

        if int(major) < 2:
            if not engine.dialect.has_schema(engine, schema_name):  # type: ignore
                getattr(engine, "execute")(sa.schema.CreateSchema(schema_name))
        else:
            with engine.begin() as connection:
                if not sa.inspect(engine).has_schema(schema_name):
                    connection.execute(sa.schema.CreateSchema(schema_name))
