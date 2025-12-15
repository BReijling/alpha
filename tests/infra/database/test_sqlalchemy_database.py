from uuid import uuid4

import pytest
from alpha.infra.database.sql_alchemy_database import SqlAlchemyDatabase
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, scoped_session

from alpha.interfaces.sql_database import SqlDatabase


@pytest.fixture
def metadata():
    return MetaData()


@pytest.fixture
def conn_str():
    return "sqlite:///:memory:"


@pytest.fixture
def car_table(metadata):
    return Table(
        "cars",
        metadata,
        Column("id", Integer, primary_key=True, unique=True, default=uuid4()),
        Column("kenteken", String, primary_key=True),
        UniqueConstraint("kenteken"),
    )


def test_database_class(metadata, conn_str, car_table):
    # Create a new Database object with the required parameters
    database = SqlAlchemyDatabase(conn_str=conn_str, create_schema=False)

    # Check that database is an instance of its interface class
    assert isinstance(database, SqlDatabase)

    # Check that the connection string is constructed correctly
    assert database._connection_string == conn_str

    # Check that the engine and session factory are created correctly
    assert isinstance(database._engine, Engine)
    assert isinstance(database._session_factory, scoped_session)

    # Check that the default schema name is set correctly
    assert database._schema_name == "public"

    # Check that the get_session() method returns a valid session
    session = database.get_session()
    assert isinstance(session, Session)

    # Check that the engine() method returns the correct engine
    assert database.engine() == database._engine

    # Check that the create_tables() method can be called and creates the car_table
    database.create_tables(metadata, tables=[car_table])

    # Check if the 'cars' table is present
    assert session.execute(text("SELECT * FROM cars"))

    # Check that the drop_tables() method can be called and drops the car_table
    database.drop_tables(metadata, tables=[car_table])

    # Check if the 'cars' table has been dropped
    with pytest.raises(OperationalError):
        assert session.execute(text("SELECT * FROM cars"))
