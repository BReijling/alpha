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
