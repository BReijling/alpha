from alpha.interfaces.providers import (
    IdentityProvider,
    TokenProvider,
    UserDirectory,
    TokenIssuer,
    TokenValidator,
    PasswordAuthenticator,
)
from alpha.providers.models.identity import Identity


def test_ldap_provider(ldap_provider):
    assert isinstance(ldap_provider, PasswordAuthenticator)
    assert isinstance(ldap_provider, UserDirectory)
    assert isinstance(ldap_provider, TokenIssuer)
    assert isinstance(ldap_provider, TokenValidator)
    assert isinstance(ldap_provider, TokenProvider)
    assert isinstance(ldap_provider, IdentityProvider)


def test_ldap_provider_authenticate(ldap_provider, credentials):
    identity = ldap_provider.authenticate(credentials)

    assert isinstance(identity, Identity)
    assert identity.subject == "ldap_user"
    assert identity.username == "ldap_user"
    assert identity.email == "ldap_user@example.com"
    assert identity.display_name == "LDAP User"


def test_ldap_provider_get_user(ldap_provider):
    identity = ldap_provider.get_user("ldap_user")

    assert isinstance(identity, Identity)
    assert identity.subject == "ldap_user"
    assert identity.username == "ldap_user"
    assert identity.email == "ldap_user@example.com"
    assert identity.display_name == "LDAP User"


def test_ad_provider_authenticate(ad_provider, credentials):
    identity = ad_provider.authenticate(credentials)

    assert isinstance(identity, Identity)
    assert identity.subject == "ldap_user"
    assert identity.username == "ldap_user"
    assert identity.email == "ldap_user@example.com"
    assert identity.display_name == "LDAP User"


def test_ad_provider_get_user(ad_provider):
    identity = ad_provider.get_user("ldap_user")

    assert isinstance(identity, Identity)
    assert identity.subject == "ldap_user"
    assert identity.username == "ldap_user"
    assert identity.email == "ldap_user@example.com"
    assert identity.display_name == "LDAP User"
