def test_permission(sample_permission):
    assert sample_permission.id is None
    assert sample_permission.name == "read"
    assert sample_permission.description == ""


def test_permission_str_and_repr(sample_permission):
    assert str(sample_permission) == "read"
    assert repr(sample_permission) == "Permission(name='read', description='')"


def test_permission_to_dict(sample_permission):
    assert sample_permission.to_dict() == {
        "id": None,
        "name": "read",
        "description": "",
        "created_by": None,
        "created_at": None,
        "modified_by": None,
        "modified_at": None,
    }


def test_permission_update(sample_permission, another_sample_permission):
    permission = sample_permission.update(another_sample_permission)

    assert permission.name == "write"
    assert permission.description == "Allows writing data"
    assert permission.modified_at is not None
