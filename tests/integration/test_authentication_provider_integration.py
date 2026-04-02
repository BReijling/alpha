import os

import pytest


def test_authentication_service_with_database_provider(
    authentication_service_with_database_provider_and_static_user,
    user_fred,
    fred_credentials,
    static_credentials,
    static_user,
    group2,
    group3,
):
    # Prepare the database with the user and groups
    uow = authentication_service_with_database_provider_and_static_user.uow

    with uow:
        fred_object = uow.users.add(user_fred)
        uow.groups.add(group2)
        uow.groups.add(group3)
        uow.commit()

    assert fred_object.groups == ["group2", "group3"]
    assert fred_object.permissions == []
    assert fred_object.admin is True

    with uow:
        # Verify that the user and groups are in the database
        assert uow.users.count() == 1
        assert uow.groups.count() == 2

    # Authenticate the user using the authentication service
    auth_token = (
        authentication_service_with_database_provider_and_static_user.login(
            credentials=fred_credentials
        )
    )

    identity = (
        authentication_service_with_database_provider_and_static_user.verify(
            auth_token
        )
    )
    assert identity.username == user_fred.username
    assert identity.email == user_fred.email
    assert identity.groups == ["group2", "group3"]
    assert identity.permissions == ["read", "write"]
    assert identity.has_admin_privileges is True

    # Authenticate the static user using the authentication service
    auth_token = (
        authentication_service_with_database_provider_and_static_user.login(
            credentials=static_credentials
        )
    )
    identity = (
        authentication_service_with_database_provider_and_static_user.verify(
            auth_token
        )
    )
    assert identity.username == static_user.username
    assert identity.email == static_user.email
    assert identity.groups == static_user.groups
    assert identity.permissions == ["read", "write"]
    assert identity.has_admin_privileges is False


@pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Unable to run KeyCloak service in GitHub Actions",
)
def test_authentication_service_with_keycloak_provider(
    authentication_service_with_keycloak_provider,
    user_alice,
    group1,
    group2,
    group3,
    keycloak_credentials,
    auth_token,
):
    # Prepare the database with the user and groups
    uow = authentication_service_with_keycloak_provider.uow

    with uow:
        alice_object = uow.users.add(user_alice)
        uow.groups.add(group1)
        uow.groups.add(group2)
        uow.groups.add(group3)
        uow.commit()

    with uow:
        # Verify that the user and groups are in the database
        assert uow.refresh_tokens.count() == 0
        assert uow.users.count() == 1
        assert uow.groups.count() == 3

    # Authenticate the user using the authentication service
    _, refresh_cookie, auth_token = (
        authentication_service_with_keycloak_provider.login(
            credentials=keycloak_credentials
        )
    )

    identity = authentication_service_with_keycloak_provider.verify(auth_token)

    assert identity.username == user_alice.username
    assert identity.email == user_alice.email
    assert group1.name in identity.groups
    assert group2.name in identity.groups
    assert group3.name not in identity.groups
    assert "read" in identity.permissions
    assert "write" in identity.permissions
    assert "admin" not in identity.permissions
    assert identity.has_admin_privileges is False

    # Verify that the refresh token is stored in the database
    with uow:
        assert uow.refresh_tokens.count() == 1

        # Add group3 to the user and verify that the token is updated with the new group
        user = uow.users.get_by_id(alice_object.id)
        user.groups = [group1.name, group2.name, group3.name]
        uow.commit()

    auth_cookie, refresh_cookie, auth_token = (
        authentication_service_with_keycloak_provider.login(
            credentials=keycloak_credentials
        )
    )

    identity = authentication_service_with_keycloak_provider.verify(auth_token)

    assert identity.username == user_alice.username
    assert identity.email == user_alice.email
    assert group1.name in identity.groups
    assert group2.name in identity.groups
    assert group3.name in identity.groups
    assert "read" in identity.permissions
    assert "write" in identity.permissions
    assert "admin" in identity.permissions
    assert identity.has_admin_privileges is True

    _, new_auth_token = (
        authentication_service_with_keycloak_provider.refresh_token(
            refresh_token=refresh_cookie.value, auth_token=auth_token
        )
    )

    identity = authentication_service_with_keycloak_provider.verify(
        new_auth_token
    )

    assert identity.username == user_alice.username
    assert identity.email == user_alice.email
    assert group1.name in identity.groups
    assert group2.name in identity.groups
    assert group3.name in identity.groups
    assert "read" in identity.permissions
    assert "write" in identity.permissions
    assert "admin" in identity.permissions


@pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Unable to run LDAP service in GitHub Actions",
)
def test_authentication_service_with_ldap_provider(
    authentication_service_with_ldap_provider,
    credentials,
):
    # Authenticate the user using the authentication service
    _, auth_token = authentication_service_with_ldap_provider.login(
        credentials=credentials
    )

    identity = authentication_service_with_ldap_provider.verify(auth_token)
    assert identity.username == "jdoe"
    assert identity.email == "jdoe@example.org"
    assert identity.display_name == "John Doe"
    assert identity.groups == []
    assert identity.permissions == []
    assert identity.has_admin_privileges is False
