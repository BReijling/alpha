def test_group(sample_group):
    assert sample_group.id is None
    assert sample_group.name == "samplegroup"
    assert sample_group.description is None


def test_group_str_and_repr(sample_group):
    assert str(sample_group) == "samplegroup"
    assert repr(sample_group) == (
        "Group(id=None, name='samplegroup', description=None)"
    )


def test_group_to_dict(sample_group):
    group_dict = sample_group.to_dict()
    assert group_dict["id"] is None
    assert group_dict["name"] == "samplegroup"
    assert group_dict["description"] is None
    assert group_dict["created_by"] is None
    assert group_dict["created_at"] is None
    assert group_dict["modified_by"] is None
    assert group_dict["modified_at"] is None


def test_group_update(sample_group, another_sample_group):
    group = sample_group.update(another_sample_group)
    assert group.name == "anothergroup"
    assert group.description == "Another sample group"


def test_group_add_remove_to_string_collections(sample_group):
    group = sample_group
    assert group.permissions == []

    group.add_permission("write")
    assert "write" in group.permissions
    group.remove_permission("write")
    assert "write" not in group.permissions


def test_group_add_remove_to_object_collections(
    group_with_object_collections,
    sample_permission,
    another_sample_permission,
):
    group = group_with_object_collections
    assert group.name == "newgroup"
    assert group.permissions == []

    group.add_permission(sample_permission)
    assert sample_permission in group.permissions

    group.add_permission(another_sample_permission)
    assert another_sample_permission in group.permissions

    group.remove_permission(sample_permission)
    assert sample_permission not in group.permissions

    group.remove_permission(another_sample_permission)
    assert another_sample_permission not in group.permissions
