import pytest

from alpha.interfaces.unit_of_work import UnitOfWork


def test_rest_api_uow_initialization(rest_api_uow):
    assert rest_api_uow._repositories is not None
    assert rest_api_uow._session is None

    assert isinstance(rest_api_uow, UnitOfWork)


def test_rest_api_uow_repository_interface_validation(
    rest_api_uow_with_invalid_repo,
):
    with pytest.raises(TypeError):
        with rest_api_uow_with_invalid_repo:
            pass


def test_rest_api_uow_context_management(rest_api_uow):
    with rest_api_uow as uow:
        assert uow.session is not None
        assert hasattr(uow, "test_repo")


def test_rest_api_uow_commit_raises_not_implemented(rest_api_uow):
    with pytest.raises(NotImplementedError):
        rest_api_uow.commit()

    with pytest.raises(NotImplementedError):
        rest_api_uow.flush()

    with pytest.raises(NotImplementedError):
        rest_api_uow.rollback()

    with pytest.raises(NotImplementedError):
        rest_api_uow.refresh(obj=None)
