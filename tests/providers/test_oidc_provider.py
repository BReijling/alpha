import pytest

from alpha.exceptions import NotSupportedException
from alpha.providers.models.identity import Identity


def test_oidc_provider(oidc_provider, credentials):

    assert oidc_provider._connector is not None
    assert oidc_provider.protocol == "oidc"


def test_oidc_provider_authenticate(oidc_provider, credentials):

    result = oidc_provider.authenticate(credentials)

    assert isinstance(result, Identity)
    assert result.subject == "oidc_user"
    assert result.username == "oidc_user"
    assert result.email == "oidc_user@example.com"
    assert result.display_name == "OIDC User"
    assert result.expires_at is None


def test_oidc_provider_get_user(oidc_provider):

    result = oidc_provider.get_user("test_subject")

    assert isinstance(result, Identity)
    assert result.subject == "test_subject"
    assert result.username == "oidc_user"
    assert result.email == "oidc_user@example.com"
    assert result.display_name == "OIDC User"


def test_oidc_provider_change_password(oidc_provider):

    with pytest.raises(NotSupportedException):
        oidc_provider.change_password("credentials", "new_password")


def test_oidc_provider_validate(oidc_provider, token):

    result = oidc_provider.validate(token)

    assert isinstance(result, Identity)
    assert result.subject == "oidc_user"
    assert result.username == "oidc_user"
    assert result.email == None
    assert result.display_name == None


def test_oidc_provider_get_claims(oidc_provider):

    test_claims = {
        "sub": "test_subject",
        "name": "Test User",
        "email": "test_user@example.com",
        "realm_access": {"roles": ["user", "admin"]},
    }

    assert (
        oidc_provider._get_claim(test_claims, "sub", "default_value")
        == "test_subject"
    )
    assert (
        oidc_provider._get_claim(test_claims, "username", "default_value")
        == "default_value"
    )

    oidc_provider._claim_mappings = {"roles": ["realm_access.roles"]}
    assert oidc_provider._get_claim(test_claims, "roles", "default_value") == [
        "user",
        "admin",
    ]
