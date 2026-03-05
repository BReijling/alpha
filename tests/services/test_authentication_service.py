import pytest
from alpha import exceptions
from alpha.providers.models.identity import Identity
from alpha.services.models.cookie import Cookie


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
    token = authentication_service.login(fake_user_credentials)
    assert token == "static_user_token"


def test_authentication_service_login_with_static_user(
    authentication_service, static_user_credentials
):
    token = authentication_service.login(static_user_credentials)
    assert token == "static_user_token"


def test_authentication_service_login_use_cookies(
    authentication_service_use_cookies, static_user_credentials
):
    cookie = authentication_service_use_cookies.login(static_user_credentials)
    assert isinstance(cookie, Cookie)
    assert (
        cookie.key
        == authentication_service_use_cookies._cookie_auth_token_name
    )
    assert cookie.value == "static_user_token"
    assert (
        cookie.max_age
        == authentication_service_use_cookies._cookie_auth_token_max_age
    )
    assert cookie.path == authentication_service_use_cookies._cookie_path
    assert cookie.domain == authentication_service_use_cookies._cookie_domain
    assert cookie.secure == authentication_service_use_cookies._cookie_secure
    assert (
        cookie.httponly == authentication_service_use_cookies._cookie_httponly
    )
    assert (
        cookie.samesite == authentication_service_use_cookies._cookie_samesite
    )


def test_authentication_service_logout(authentication_service):
    result = authentication_service.logout(None)
    assert result == "Logout successful"


def test_authentication_service_logout_use_cookies(
    authentication_service_use_cookies,
):
    cookie = authentication_service_use_cookies.logout(None)
    assert isinstance(cookie, Cookie)
    assert cookie.operation == "delete"


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
