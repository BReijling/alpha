from alpha.interfaces.sql_repository import SqlRepository


def test_sql_alchemy_repository(sql_alchemy_repository):
    assert isinstance(sql_alchemy_repository, SqlRepository)
    assert sql_alchemy_repository is not None
    assert sql_alchemy_repository.session is not None
    assert sql_alchemy_repository._default_model == "Model"
