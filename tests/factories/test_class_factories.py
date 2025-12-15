from datetime import datetime

import pytest
from alpha import exceptions

from alpha.interfaces.dataclass_instance import DataclassInstance
from alpha.interfaces.factories import (
    ClassFactory,
    DefaultFactory,
    FactoryClassesInstance,
)
from tests.fixtures._domain_models import User
from tests.fixtures.fake_factory_classes import FakeDataclass


def test_iterable_class_factory(
    iterable_class_factory: ClassFactory,
    fake_all_type_class: DataclassInstance,
    factory_classes: FactoryClassesInstance,
):

    obj = fake_all_type_class
    fields = getattr(fake_all_type_class, "__dataclass_fields__")

    result = iterable_class_factory.process(
        obj=obj,
        field=fields["list_dataclass"],
        factory_classes=factory_classes,
    )
    assert isinstance(result, list)
    assert isinstance(result[0], str)
    assert result[0] == "model"

    result = iterable_class_factory.process(
        obj=obj,
        field=fields["no_list_dataclass"],
        factory_classes=factory_classes,
    )
    assert isinstance(result, list)
    assert isinstance(result[0], str)
    assert result[0] == "model"

    result = iterable_class_factory.process(
        obj=obj, field=fields["types_list"], factory_classes=factory_classes
    )
    assert isinstance(result, list)
    assert isinstance(result[0], str)
    assert result[0] == "abc"

    result = iterable_class_factory.process(
        obj=obj, field=fields["optional_list"], factory_classes=factory_classes
    )
    assert result == "optional_list"

    assert isinstance(
        iterable_class_factory.process(
            obj=obj, field=fields["types_list"], factory_classes=None
        ),
        list,
    )
    assert isinstance(
        iterable_class_factory.process(
            obj=obj, field=fields["typing_list"], factory_classes=None
        ),
        list,
    )
    assert isinstance(
        iterable_class_factory.process(
            obj=obj, field=fields["types_tuple"], factory_classes=None
        ),
        tuple,
    )
    assert isinstance(
        iterable_class_factory.process(
            obj=obj, field=fields["typing_tuple"], factory_classes=None
        ),
        tuple,
    )
    assert isinstance(
        iterable_class_factory.process(
            obj=obj, field=fields["types_set"], factory_classes=None
        ),
        set,
    )
    assert isinstance(
        iterable_class_factory.process(
            obj=obj, field=fields["typing_set"], factory_classes=None
        ),
        set,
    )
    enum_list = iterable_class_factory.process(
        obj=obj, field=fields["enum_list"], factory_classes=factory_classes
    )
    assert isinstance(enum_list, list)
    assert enum_list[0] == "enum"

    with pytest.raises(exceptions.TypingFactoryException):
        iterable_class_factory.process(
            obj=obj, field=fields["types_dict"], factory_classes=None
        )


def test_dict_class_factory(
    dict_class_factory: ClassFactory,
    fake_dict_factory_class: DataclassInstance,
):

    obj = fake_dict_factory_class(obj={"name": "name"})
    fields = getattr(fake_dict_factory_class, "__dataclass_fields__")

    assert dict_class_factory.process(
        obj=obj, field=fields["obj"], factory_classes=None
    ) == {"name": "name"}
    assert (
        dict_class_factory.process(
            obj=obj, field=fields["to_dict_param"], factory_classes=None
        )
        == "to_dict"
    )
    assert (
        dict_class_factory.process(
            obj=obj, field=fields["asdict_param"], factory_classes=None
        )
        == "_asdict"
    )
    assert (
        dict_class_factory.process(
            obj=obj, field=fields["dict_param"], factory_classes=None
        )
        == "__dict__"
    )

    with pytest.raises(exceptions.ObjectConversionError):
        assert dict_class_factory.process(
            obj=obj, field=fields["string_param"], factory_classes=None
        )


def test_dataclass_class_factory(
    api_address,
    api_address_nested,
    dataclass_class_factory: ClassFactory,
    factory_classes: FactoryClassesInstance,
):

    fields = getattr(User, "__dataclass_fields__")

    # Testing a normal object containing the same attributes as
    # the Address class
    obj = dataclass_class_factory.process(
        obj=api_address,
        field=fields["address"],
        factory_classes=factory_classes,
    )
    assert obj == "model"

    # Testing an object with a address attribute which contains an object
    # with the Address attributes
    obj = dataclass_class_factory.process(
        obj=api_address_nested,
        field=fields["address"],
        factory_classes=factory_classes,
    )
    assert obj == "model"


def test_default_field_factory(default_fields, default_field_factory: DefaultFactory):

    string_default = default_field_factory.process(
        field=default_fields["string_default"]
    )
    list_factory = default_field_factory.process(field=default_fields["list_factory"])
    date_time = default_field_factory.process(field=default_fields["date_time"])

    assert string_default == "string"
    assert list_factory == []
    assert isinstance(date_time, datetime)

    with pytest.raises(exceptions.DefaultFactoryException):
        default_field_factory.process(field=default_fields["no_default"])
        default_field_factory.process(field=default_fields["none_default"])


def test_generic_alias_class_factory(
    generic_alias_class_factory: ClassFactory,
    fake_all_type_class: DataclassInstance,
    factory_classes: FactoryClassesInstance,
):

    cls = fake_all_type_class
    fields = cls.__dataclass_fields__

    assert (
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["types_list"],
            factory_classes=factory_classes,
        )
        == "iterable"
    )
    assert (
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["typing_list"],
            factory_classes=factory_classes,
        )
        == "iterable"
    )
    assert (
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["types_tuple"],
            factory_classes=factory_classes,
        )
        == "iterable"
    )
    assert (
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["typing_tuple"],
            factory_classes=factory_classes,
        )
        == "iterable"
    )
    assert (
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["types_set"],
            factory_classes=factory_classes,
        )
        == "iterable"
    )
    assert (
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["typing_set"],
            factory_classes=factory_classes,
        )
        == "iterable"
    )
    assert (
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["types_dict"],
            factory_classes=factory_classes,
        )
        == "dict"
    )
    assert (
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["typing_dict"],
            factory_classes=factory_classes,
        )
        == "dict"
    )

    with pytest.raises(exceptions.MixedArgumentTypesError):
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["types_list_union"],
            factory_classes=None,
        )
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["typing_list_union"],
            factory_classes=None,
        )

    with pytest.raises(exceptions.TypingFactoryException):
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["str_"],
            factory_classes=None,
        )
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["int_"],
            factory_classes=None,
        )
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["float_"],
            factory_classes=None,
        )
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["complex_"],
            factory_classes=None,
        )
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["bool_"],
            factory_classes=None,
        )
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["date_"],
            factory_classes=None,
        )
        generic_alias_class_factory.process(
            obj=cls,
            field=fields["datetime_"],
            factory_classes=None,
        )


def test_union_class_factory(
    union_class_factory: ClassFactory,
    fake_all_type_class: DataclassInstance,
    factory_classes: FactoryClassesInstance,
):

    obj = fake_all_type_class
    fields = fake_all_type_class.__dataclass_fields__

    assert (
        union_class_factory.process(
            obj=obj,
            field=fields["types_union"],
            factory_classes=factory_classes,
        )
        == 1
    )
    assert (
        union_class_factory.process(
            obj=obj,
            field=fields["typing_union"],
            factory_classes=factory_classes,
        )
        == 1
    )
    assert (
        union_class_factory.process(
            obj=obj,
            field=fields["types_union2"],
            factory_classes=factory_classes,
        )
        == "generic"
    )
    assert (
        union_class_factory.process(
            obj=obj,
            field=fields["no_str"],
            factory_classes=factory_classes,
        )
        == "no_str"
    )
    assert (
        union_class_factory.process(
            obj=obj,
            field=fields["optional_dataclass"],
            factory_classes=factory_classes,
        )
        == "model"
    )


def test_native_class_factory(
    native_class_factory: ClassFactory,
    fake_all_type_class: DataclassInstance,
    factory_classes: FactoryClassesInstance,
):

    obj = fake_all_type_class
    fields = fake_all_type_class.__dataclass_fields__

    assert (
        native_class_factory.process(
            obj=obj, field=fields["str_"], factory_classes=factory_classes
        )
        == "abc"
    )
    assert (
        native_class_factory.process(
            obj=obj, field=fields["int_"], factory_classes=factory_classes
        )
        == 1
    )
    assert (
        native_class_factory.process(
            obj=obj, field=fields["float_"], factory_classes=factory_classes
        )
        == 0.1
    )
    assert (
        native_class_factory.process(
            obj=obj, field=fields["no_str"], factory_classes=factory_classes
        )
        == "no_str"
    )
    assert isinstance(
        native_class_factory.process(
            obj=obj,
            field=fields["dataclass_"],
            factory_classes=factory_classes,
        ),
        FakeDataclass,
    )
    assert isinstance(
        native_class_factory.process(
            obj=obj,
            field=fields["dataclass_"],
            factory_classes=factory_classes,
        ),
        FakeDataclass,
    )
    assert (
        native_class_factory.process(
            obj=obj,
            field=fields["json_patch"],
            factory_classes=factory_classes,
        )
        == "json_patch"
    )

    # Check for backwards compatibility for python 3.9/10 by using a field with
    # a list type
    assert (
        native_class_factory.process(
            obj=obj,
            field=fields["typing_list"],
            factory_classes=factory_classes,
        )
        == "generic_alias"
    )


def test_enum_class_factory(
    enum_class_factory: ClassFactory,
    fake_dataclass: DataclassInstance,
    factory_classes: FactoryClassesInstance,
):

    cls = fake_dataclass()
    field = cls.__dataclass_fields__["field"]

    assert (
        enum_class_factory.process(
            obj=cls, field=field, factory_classes=factory_classes
        )
        == "enum"
    )


def test_json_patch_class_factory(
    json_patch_class_factory: ClassFactory,
    fake_dataclass: DataclassInstance,
    factory_classes: FactoryClassesInstance,
):

    cls = fake_dataclass()
    field = cls.__dataclass_fields__["field"]

    assert (
        json_patch_class_factory.process(
            obj=cls, field=field, factory_classes=factory_classes
        )
        == "json_patch"
    )


def test_any_class_factory(
    any_class_factory: ClassFactory,
    fake_dataclass: DataclassInstance,
    factory_classes: FactoryClassesInstance,
):

    cls = fake_dataclass()
    field = cls.__dataclass_fields__["field"]

    assert (
        any_class_factory.process(obj=cls, field=field, factory_classes=factory_classes)
        == "field"
    )

    cls = fake_dataclass(field=None)
    field = cls.__dataclass_fields__["field"]

    assert (
        any_class_factory.process(obj=cls, field=field, factory_classes=factory_classes)
        == "field"
    )
