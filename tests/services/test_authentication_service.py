import pytest
from alpha import exceptions
from alpha.providers.models.identity import Identity
from tests.services.conftest import authentication_service


def test_authentication_service_init(authentication_service, fake_static_user):
    assert authentication_service._identity_provider is not None
    assert authentication_service._identity_id_attribute == "subject"
    assert authentication_service._merge_with_database_users is False
    assert authentication_service._user_id_attribute == "username"
    assert authentication_service.uow is not None
    assert (
        authentication_service._users_repository_name
        == "authentication_service"
    )
    assert authentication_service._static_user == fake_static_user


def test_authentication_service_login(
    authentication_service, fake_user_credentials
):
    credentials = fake_user_credentials
    token = authentication_service.login(credentials)
    assert token == "static_user_token"


def test_authentication_service_login_with_static_user(
    authentication_service, static_user_credentials
):
    credentials = static_user_credentials
    token = authentication_service.login(credentials)
    assert token == "static_user_token"


def test_authentication_service_logout(authentication_service):
    result = authentication_service.logout(None)
    assert result == "Logout successful"


def test_authentication_service_change_password(
    authentication_service, fake_user_credentials
):
    new_password = "new_fake_password"
    authentication_service.change_password(fake_user_credentials, new_password)
    # Since we're using a fake provider, we can't verify the password change
    # directly. In a real test, you would check that the password was updated
    # in the identity provider or database.
    assert (
        authentication_service._identity_provider._new_password == new_password
    )


def test_authentication_service_verify(authentication_service, identity):
    result = authentication_service.verify(None)
    assert isinstance(result, Identity)


def test_authentication_service_pretend_login(
    authentication_service, identity
):
    pretend_subject = "fake_subject"
    # authentication_service._identity_provider._identity = Identity.from_dict(
    #     {
    #         "subject": pretend_subject,
    #         "groups": ["group3", "group4"],
    #         "permissions": ["modify", "delete"],
    #         "role": "TESTER",
    #         "admin": True,
    #     }
    # )

    with pytest.raises(exceptions.UnauthorizedException):
        authentication_service.pretend_login(
            identity=identity, pretend_subject=pretend_subject
        )

    identity.admin = True

    with pytest.raises(exceptions.NotFoundException):
        authentication_service.pretend_login(
            identity=identity, pretend_subject="pretend_subject"
        )

    token = authentication_service.pretend_login(
        identity=identity, pretend_subject=pretend_subject
    )

    assert isinstance(token, str)
    assert token == "static_user_token"


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

    authentication_service.uow = None

    with pytest.raises(exceptions.MissingDependencyException):
        authentication_service._merge_identity_with_user(identity=identity)
