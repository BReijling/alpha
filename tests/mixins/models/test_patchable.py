import pytest


def test_patch_method(
    fake_model,
    patch_remove_name,
    patch_remove_description,
    patch_replace_name,
    patch_replace_description,
    patch_add_to_collection,
    patch_remove_from_collection,
    patch_add_name,
    patch_add_description,
):
    assert fake_model.name == "name"
    assert fake_model.description == "description"
    assert fake_model.collection == []

    fake_model.patch(patch_add_name)
    assert fake_model.name == "added name"

    fake_model.patch(patch_add_description)
    assert fake_model.description == "added description"

    fake_model.patch(patch_replace_name)
    assert fake_model.name == "replaced name"

    fake_model.patch(patch_replace_description)
    assert fake_model.description == "replaced description"

    fake_model.patch(patch_add_to_collection)
    assert "item" in fake_model.collection

    fake_model.patch(patch_remove_from_collection)
    assert "item" not in fake_model.collection

    fake_model.patch(patch_remove_name)
    assert fake_model.name is None

    fake_model.patch(patch_remove_description)
    assert fake_model.description is None


def test_patch_exceptions(fake_model, another_fake_model):
    with pytest.raises(AttributeError):
        another_fake_model.patch("invalid_object")

    with pytest.raises(ValueError):
        fake_model.patch({"op": "invalid", "path": "/name", "value": "value"})

    with pytest.raises(NotImplementedError):
        another_fake_model.__patch_fields__
