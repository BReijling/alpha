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
