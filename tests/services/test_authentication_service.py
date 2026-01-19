def test_authentication_service_merge_identity_with_user(
    authentication_service, identity
):
    assert "group3" not in identity.groups
    assert "group4" not in identity.groups
    assert "modify" not in identity.permissions
    assert "delete" not in identity.permissions
    assert identity.role == "SUPERUSER"
    assert identity.admin is False

    merged_identity = authentication_service._merge_identity_with_user(
        identity=identity
    )

    assert merged_identity is not None
    assert "group3" in merged_identity.groups
    assert "group4" in merged_identity.groups
    assert "modify" in merged_identity.permissions
    assert "delete" in merged_identity.permissions
    assert merged_identity.role == "TESTER"
    assert merged_identity.admin is True
