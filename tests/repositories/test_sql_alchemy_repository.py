def test_sql_alchemy_repository(sql_alchemy_repository):
    assert sql_alchemy_repository is not None
    assert sql_alchemy_repository.session is not None
    assert sql_alchemy_repository._default_model == "Model"
