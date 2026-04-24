"""SQL Alchemy Database Connector module"""

import sqlalchemy as sa
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.orm.session import Session

from alpha.interfaces.sql_mapper import SqlMapper


class SqlAlchemyDatabase:
    """SQL Alchemy Database Connector class. This class provides methods to
    connect to a SQL database using SQL Alchemy, manage sessions, and create or
    drop tables based on SQL Alchemy metadata. It supports connection
    configuration through either individual parameters or a connection string.
    The class also includes functionality to create a database schema if it
    does not exist.

    Parameters
    ----------
    host
        Hostname of the database server, by default ""
    port
        Port number of the database server, by default None
    username
        Username for the database, by default ""
    password
        Password for the database, by default ""
    db_name
        Database name, by default ""
    db_type
        Database type, by default "postgresql"
    conn_str
        Connection string. Can be used instead of host, port, username,
        password, and db_name, by default None
    schema_name
        Schema name, by default "public"
    create_schema
        Whether to create the schema if it does not exist, by default True
    create_tables
        Whether to create tables if they do not exist, by default True
    pool_pre_ping
        Whether to enable pool pre-ping, by default True
    mapper
        SQL Mapper instance, by default None
    """

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
        pool_pre_ping: bool = True,
        mapper: SqlMapper | None = None,
    ) -> None:
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
            sessionmaker(
                bind=self._engine, autocommit=False, expire_on_commit=False
            )
        )

        if self._mapper:
            if not self._mapper.started:
                self._mapper.start_mapping()
            if create_tables:
                self.create_tables(self._mapper.metadata)

        if hasattr(self._engine.dialect, "has_schema") & create_schema:
            self._create_schema(self._engine, self._schema_name)

    def get_session(self) -> Session:
        """Get a new SQL Alchemy session

        Returns
        -------
        Session
            SQL Alchemy session instance
        """
        return self._session_factory()

    def engine(self) -> Engine:
        """Get the SQL Alchemy engine

        Returns
        -------
        Engine
            SQL Alchemy engine instance
        """
        return self._engine

    def create_tables(
        self, metadata: sa.MetaData, tables: list[sa.Table] | None = None
    ) -> None:
        """Create tables in the database

        Parameters
        ----------
        metadata
            SQL Alchemy MetaData instance
        tables
            List of tables to create, by default None
        """
        metadata.create_all(self._engine, tables=tables)

    def drop_tables(
        self, metadata: sa.MetaData, tables: list[sa.Table] | None = None
    ) -> None:
        """Drop tables from the database

        Parameters
        ----------
        metadata
            SQL Alchemy MetaData instance
        tables
            List of tables to drop, by default None
        """
        metadata.drop_all(self._engine, tables=tables)

    def _create_schema(self, engine: Engine, schema_name: str) -> None:
        """Create a schema in the database if it does not exist

        Parameters
        ----------
        engine
            SQL Alchemy engine instance
        schema_name
            Schema name to create
        """
        major, *_ = sa.__version__.split(".")

        if int(major) < 2:
            if not engine.dialect.has_schema(engine, schema_name):  # type: ignore
                getattr(engine, "execute")(sa.schema.CreateSchema(schema_name))
        else:
            with engine.begin() as connection:
                if not sa.inspect(engine).has_schema(schema_name):
                    connection.execute(sa.schema.CreateSchema(schema_name))
