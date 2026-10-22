def test_user(sample_user):
    assert sample_user.id is None
    assert sample_user.username == "sampleuser"
    assert sample_user.email == "sampleuser@example.com"
    assert sample_user.groups == []
    assert sample_user.permissions == []


def test_user_str_and_repr(sample_user):
    assert str(sample_user) == "sampleuser"
    assert repr(sample_user) == (
        "User("
        "id=None, "
        "username='sampleuser', "
        "display_name=None, "
        "permissions=[], "
        "groups=[]"
        ")"
    )


def test_user_from_identity(sample_user, identity):
    user_from_identity = sample_user.from_identity(identity)
    assert user_from_identity.id == identity.subject
    assert user_from_identity.username == identity.username
    assert user_from_identity.email == identity.email
    assert user_from_identity.display_name == identity.display_name
    assert user_from_identity.groups == []
    assert user_from_identity.permissions == []


def test_user_update_from_identity(sample_user, identity):
    assert sample_user.email != identity.email
    assert sample_user.display_name != identity.display_name

    sample_user.update_from_identity(identity)
    assert sample_user.email == identity.email
    assert sample_user.display_name == identity.display_name


def test_user_to_dict(sample_user):
    user_dict = sample_user.to_dict()
    assert user_dict["id"] is None
    assert user_dict["username"] == "sampleuser"
    assert user_dict["email"] == "sampleuser@example.com"
    assert user_dict["display_name"] is None
    assert user_dict["groups"] == []
    assert user_dict["permissions"] == []
    assert user_dict["created_by"] is None
    assert user_dict["created_at"] is None
    assert user_dict["modified_by"] is None
    assert user_dict["modified_at"] is None


def test_user_update(sample_user, another_sample_user):
    user = sample_user.update(another_sample_user)
    assert user.username == "anotheruser"
    assert user.email == "anotheruser@example.com"
    assert user.display_name is None
    assert user.groups == ["group1"]
    assert user.permissions == ["read"]


def test_user_add_remove_to_string_collections(user_with_string_collections):
    user = user_with_string_collections
    assert user.username == "user"
    assert user.email == "user@example.com"
    assert user.groups == []
    assert user.permissions == []

    user.add_permission("write")
    assert "write" in user.permissions
    user.remove_permission("write")
    assert "write" not in user.permissions

    user.add_group("group1")
    assert "group1" in user.groups
    user.remove_group("group1")
    assert "group1" not in user.groups


def test_user_add_remove_to_object_collections(
    user_with_object_collections,
    sample_group,
    another_sample_group,
    sample_permission,
    another_sample_permission,
):
    user = user_with_object_collections
    assert user.username == "newuser"
    assert user.email == "newuser@example.com"
    assert user.groups == []
    assert user.permissions == []

    user.add_permission(sample_permission)
    assert sample_permission in user.permissions

    user.add_permission(another_sample_permission)
    assert another_sample_permission in user.permissions

    user.add_group(sample_group)
    assert sample_group in user.groups

    user.add_group(another_sample_group)
    assert another_sample_group in user.groups

    user.remove_permission(sample_permission)
    assert sample_permission not in user.permissions

    user.remove_permission(another_sample_permission)
    assert another_sample_permission not in user.permissions

    user.remove_group(sample_group)
    assert sample_group not in user.groups

    user.remove_group(another_sample_group)
    assert another_sample_group not in user.groups
