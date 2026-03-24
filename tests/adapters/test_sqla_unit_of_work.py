import pytest
from sqlalchemy.orm.exc import UnmappedInstanceError

from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.exceptions import DatabaseSessionError


def test_sql_alchemy_uow_initialization(sql_alchemy_uow):
    assert sql_alchemy_uow._db is not None
    assert sql_alchemy_uow._repositories is not None
    assert sql_alchemy_uow.session is None

    assert isinstance(sql_alchemy_uow, UnitOfWork)

    with pytest.raises(DatabaseSessionError):
        sql_alchemy_uow.commit()
    with pytest.raises(DatabaseSessionError):
        sql_alchemy_uow.flush()
    with pytest.raises(DatabaseSessionError):
        sql_alchemy_uow.rollback()
    with pytest.raises(DatabaseSessionError):
        sql_alchemy_uow.refresh(obj=None)


def test_sql_alchemy_uow_repository_interface_validation(
    sql_alchemy_uow_with_invalid_repo,
):
    with pytest.raises(TypeError):
        with sql_alchemy_uow_with_invalid_repo:
            pass


def test_sql_alchemy_uow_context_management(sql_alchemy_uow):
    with sql_alchemy_uow as uow:
        assert uow.session is not None
        assert hasattr(uow, "test_repo")

        assert uow.commit() is None
        assert uow.flush() is None
        assert uow.rollback() is None

        with pytest.raises(UnmappedInstanceError):
            assert uow.refresh(obj=None) is None
