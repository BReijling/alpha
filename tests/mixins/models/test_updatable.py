import pytest


def test_update_method(fake_model, updated_fake_model):
    assert fake_model.name == "name"
    assert fake_model.description == "description"
    assert fake_model.modified_at is None
    assert fake_model.updated_at is None

    fake_model.update(updated_fake_model)
    assert fake_model.name == "updated name"
    assert fake_model.description == "updated description"
    assert fake_model.modified_at is not None
    assert fake_model.updated_at is not None


def test_update_exceptions(another_fake_model):
    with pytest.raises(TypeError):
        another_fake_model.update("invalid_object")

    with pytest.raises(NotImplementedError):
        another_fake_model.__update_fields__
