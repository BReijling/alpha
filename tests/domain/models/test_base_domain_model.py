import pytest


def test_base_domain_model_dataclass(native_data_class):
    assert hasattr(native_data_class, "__dataclass_fields__")
    assert hasattr(native_data_class, "to_dict")
    obj = native_data_class.to_dict()
    assert obj["id"] == native_data_class.id
    assert obj["string"] == native_data_class.string
    assert obj["integer"] == native_data_class.integer
    assert obj["optional_float"] == native_data_class.optional_float

    with pytest.raises(NotImplementedError):
        native_data_class.update(None)


def test_base_domain_model_attrs_class(attrs_class):
    assert hasattr(attrs_class, "__attrs_attrs__")
    assert hasattr(attrs_class, "to_dict")
    obj = attrs_class.to_dict()
    assert obj["id"] == attrs_class.id
    assert obj["string"] == attrs_class.string
    assert obj["integer"] == attrs_class.integer
    assert obj["optional_float"] == attrs_class.optional_float


def test_base_domain_model_pydantic_data_class(pydantic_data_class):
    assert hasattr(pydantic_data_class, "__dataclass_fields__")
    assert hasattr(pydantic_data_class, "to_dict")
    obj = pydantic_data_class.to_dict()
    assert obj["id"] == pydantic_data_class.id
    assert obj["string"] == pydantic_data_class.string
    assert obj["integer"] == pydantic_data_class.integer
    assert obj["optional_float"] == pydantic_data_class.optional_float


def test_base_domain_model_pydantic_model(pydantic_model):
    assert hasattr(pydantic_model, "__pydantic_fields__")
    assert hasattr(pydantic_model, "to_dict")
    obj = pydantic_model.to_dict()
    assert obj["id"] == pydantic_model.id
    assert obj["string"] == pydantic_model.string
    assert obj["integer"] == pydantic_model.integer
    assert obj["optional_float"] == pydantic_model.optional_float


def test_base_domain_model_another_data_model(another_data_model):
    assert not hasattr(another_data_model, "__dataclass_fields__")
    assert hasattr(another_data_model, "to_dict")
    obj = another_data_model.to_dict()
    assert obj["_id"] == str(another_data_model._id)
    assert obj["string"] == another_data_model.string
    assert obj["integer"] == another_data_model.integer
    assert obj["optional_float"] == another_data_model.optional_float


def test_base_domain_model_another_data_model_with_slots(
    another_data_model_with_slots,
):
    assert hasattr(another_data_model_with_slots, "__slots__")
    assert hasattr(another_data_model_with_slots, "to_dict")
    obj = another_data_model_with_slots.to_dict()
    assert obj["id"] == another_data_model_with_slots.id
    assert obj["string"] == another_data_model_with_slots.string
    assert obj["integer"] == another_data_model_with_slots.integer
    assert (
        obj["optional_float"] == another_data_model_with_slots.optional_float
    )
