def test_from_dict_mixin(native_data_class_dict, native_data_class):
    NativeDataClass = native_data_class.__class__
    obj = NativeDataClass.from_dict(native_data_class_dict)
    assert obj.id == native_data_class.id
    assert obj.string == native_data_class.string
    assert obj.integer == native_data_class.integer
    assert obj.optional_float == native_data_class.optional_float
