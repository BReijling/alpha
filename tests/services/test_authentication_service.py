import pytest
from alpha import exceptions
from alpha.providers.models.identity import Identity
from alpha.services.authentication_service import AuthenticationService
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

    with pytest.raises(ValueError):
        AuthenticationService(
            identity_provider=None,
            use_cookies=False,
            use_refresh_tokens=True,
        )


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
    result = authentication_service_use_cookies.login(static_user_credentials)

    assert isinstance(result, tuple)

    cookie, token = result

    assert isinstance(token, str)
    assert token == "static_user_token"

    assert isinstance(cookie, Cookie)
    assert (
        cookie.key
        == authentication_service_use_cookies._cookie_auth_token_name
    )
    assert cookie.value == "static_user_token"
    assert (
        cookie.max_age
        == authentication_service_use_cookies._auth_token_max_age
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

    with pytest.raises(exceptions.MissingConfigurationException):
        authentication_service_use_cookies.refresh_token(
            refresh_token="fake_refresh_token"
        )


def test_authentication_service_use_refresh_tokens(
    authentication_service_use_refresh_tokens,
    static_user_credentials,
    test_identity,
):
    result = authentication_service_use_refresh_tokens.login(
        static_user_credentials
    )

    assert isinstance(result, tuple)
    assert len(result) == 3

    cookie, refresh_cookie, token = result

    assert isinstance(token, str)
    assert token == "static_user_token"

    assert isinstance(cookie, Cookie)
    assert isinstance(refresh_cookie, Cookie)

    assert (
        refresh_cookie.key
        == authentication_service_use_refresh_tokens._cookie_refresh_token_name
    )
    assert len(refresh_cookie.value) == 28
    assert refresh_cookie.max_age == 3600

    result = authentication_service_use_refresh_tokens.refresh_token(
        refresh_token=refresh_cookie.value, identity=test_identity
    )

    assert isinstance(result, tuple)
    assert len(result) == 2

    new_cookie, new_token = result

    assert isinstance(new_token, str)
    assert new_token == "static_user_token"
    assert isinstance(new_cookie, Cookie)
    assert (
        new_cookie.key
        == authentication_service_use_refresh_tokens._cookie_auth_token_name
    )
    assert new_cookie.value == "static_user_token"
    assert (
        new_cookie.max_age
        == authentication_service_use_refresh_tokens._auth_token_max_age
    )

    with pytest.raises(exceptions.UnauthorizedException):
        authentication_service_use_refresh_tokens.refresh_token(
            refresh_token=refresh_cookie.value
        )


def test_authentication_service_use_refresh_tokens_database(
    authentication_service_use_refresh_tokens_database,
    static_user_credentials,
    test_identity,
):
    result = authentication_service_use_refresh_tokens_database.login(
        static_user_credentials
    )

    assert isinstance(result, tuple)
    assert len(result) == 3

    _, refresh_cookie, _ = result

    assert isinstance(refresh_cookie, Cookie)

    result = authentication_service_use_refresh_tokens_database.refresh_token(
        refresh_token=refresh_cookie.value, identity=test_identity
    )

    assert isinstance(result, tuple)
    assert len(result) == 2

    new_cookie, new_token = result

    assert isinstance(new_token, str)
    assert new_token == "static_user_token"
    assert isinstance(new_cookie, Cookie)
    assert (
        new_cookie.key
        == authentication_service_use_refresh_tokens_database._cookie_auth_token_name
    )
    assert new_cookie.value == "static_user_token"
    assert (
        new_cookie.max_age
        == authentication_service_use_refresh_tokens_database._auth_token_max_age
    )

    authentication_service_use_refresh_tokens_database.uow = None

    with pytest.raises(exceptions.MissingDependencyException):
        authentication_service_use_refresh_tokens_database.refresh_token(
            refresh_token=refresh_cookie.value, identity=test_identity
        )


def test_authentication_service_use_refresh_tokens_memory(
    authentication_service_use_refresh_tokens_memory,
    static_user_credentials,
    test_identity,
):
    result = authentication_service_use_refresh_tokens_memory.login(
        static_user_credentials,
    )

    assert isinstance(result, tuple)
    assert len(result) == 3

    cookie, refresh_cookie, token = result

    result = authentication_service_use_refresh_tokens_memory.refresh_token(
        refresh_token=refresh_cookie.value, identity=test_identity
    )

    assert isinstance(result, tuple)
    assert len(result) == 2

    new_cookie, new_token = result

    assert isinstance(new_token, str)
    assert new_token == "static_user_token"
    assert isinstance(new_cookie, Cookie)


def test_authentication_service_use_refresh_tokens_invalid_refresh_token(
    authentication_service_use_refresh_tokens, test_identity
):
    with pytest.raises(exceptions.UnauthorizedException):
        authentication_service_use_refresh_tokens.refresh_token(
            refresh_token="invalid_refresh_token", identity=test_identity
        )


def test_authentication_service_use_refresh_tokens_expired(
    authentication_service_use_refresh_tokens_memory_expired,
    static_user_credentials,
    test_identity,
):
    result = authentication_service_use_refresh_tokens_memory_expired.login(
        static_user_credentials
    )

    with pytest.raises(exceptions.TokenExpiredException):
        authentication_service_use_refresh_tokens_memory_expired.refresh_token(
            refresh_token=result[1].value, identity=test_identity
        )


def test_authentication_service_invalid_refresh_token_storage(
    authentication_service,
):
    with pytest.raises(exceptions.InvalidAttributeError):
        authentication_service._create_refresh_token("test")

    with pytest.raises(exceptions.InvalidAttributeError):
        authentication_service._get_refresh_token_from_storage("test")


def test_authentication_service_logout(authentication_service):
    with pytest.raises(NotImplementedError):
        authentication_service.logout(None)


def test_authentication_service_logout_use_cookies(
    authentication_service_use_cookies,
):
    cookie, _ = authentication_service_use_cookies.logout(None)
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


def test_authentication_service_verify(authentication_service):
    result = authentication_service.verify(None)
    assert isinstance(result, Identity)


def test_authentication_service_pretend_login(
    authentication_service, authentication_service_use_cookies, test_identity
):
    pretend_subject = "fake_subject"

    with pytest.raises(exceptions.UnauthorizedException):
        authentication_service.pretend_login(
            identity=test_identity, pretend_subject=pretend_subject
        )

    test_identity.admin = True

    with pytest.raises(exceptions.NotFoundException):
        authentication_service.pretend_login(
            identity=test_identity, pretend_subject="pretend_subject"
        )

    token = authentication_service.pretend_login(
        identity=test_identity, pretend_subject=pretend_subject
    )

    assert isinstance(token, str)
    assert token == "static_user_token"

    auth_cookie, token = authentication_service_use_cookies.pretend_login(
        identity=test_identity, pretend_subject=pretend_subject
    )

    assert isinstance(token, str)
    assert token == "static_user_token"
    assert isinstance(auth_cookie, Cookie)
    assert (
        auth_cookie.key
        == authentication_service_use_cookies._cookie_auth_token_name
    )
    assert auth_cookie.value == "static_user_token"


def test_authentication_service_merge_identity_with_user(
    authentication_service,
    test_identity,
):
    assert "group3" not in test_identity.groups
    assert "group4" not in test_identity.groups
    assert "modify" not in test_identity.permissions
    assert "delete" not in test_identity.permissions
    assert test_identity.role == "SUPERUSER"
    assert test_identity.admin is False

    merged_identity = authentication_service._merge_identity_with_user(
        identity=test_identity
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
        authentication_service._merge_identity_with_user(
            identity=test_identity
        )


def test_authentication_service_merge_identity_with_groups(
    authentication_service_merge_groups,
    identity_for_groups,
):
    merged_identity = (
        authentication_service_merge_groups._merge_identity_with_user(
            identity=identity_for_groups
        )
    )

    assert merged_identity is not None
    assert "group1" in merged_identity.groups
    assert "group2" in merged_identity.groups
    assert "group3" in merged_identity.groups
    assert "group4" in merged_identity.groups
    assert "group5" in merged_identity.groups
    assert "group6" in merged_identity.groups

    merged_identity = (
        authentication_service_merge_groups._merge_identity_with_groups(
            identity=identity_for_groups
        )
    )

    assert "read" in merged_identity.permissions
    assert "write" in merged_identity.permissions
    assert "modify" in merged_identity.permissions
    assert "delete" in merged_identity.permissions
    assert "append" in merged_identity.permissions
    assert "create" in merged_identity.permissions
    assert "admin" in merged_identity.permissions
