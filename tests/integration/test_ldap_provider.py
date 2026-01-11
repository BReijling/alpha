import os
import pytest

from alpha.providers.models.identity import Identity
from alpha.providers.models.credentials import PasswordCredentials


@pytest.mark.skipif(
    os.getenv('GITHUB_ACTIONS') == 'true',
    reason='Unable to run LDAP service in GitHub Actions',
)
def test_ldap_provider_authentication(ldap_provider, credentials):
    identity = ldap_provider.authenticate(credentials=credentials)

    assert isinstance(identity, Identity)
    assert identity.subject == 'jdoe'
    assert identity.username == 'jdoe'
    assert identity.email == 'jdoe@example.org'
    assert identity.display_name == 'John Doe'
    assert identity.groups == []


@pytest.mark.skipif(
    os.getenv('GITHUB_ACTIONS') == 'true',
    reason='Unable to run LDAP service in GitHub Actions',
)
def test_ldap_provider_get_user(ldap_provider, subject):
    identity = ldap_provider.get_user(subject=subject)

    assert isinstance(identity, Identity)
    assert identity.subject == 'jdoe'
    assert identity.username == 'jdoe'
    assert identity.email == 'jdoe@example.org'
    assert identity.display_name == 'John Doe'
    assert identity.groups == []


# def test_ldap_provider_change_password(ldap_provider, subject):
#     new_password = 'newpassword123'
#     ldap_provider.change_password(subject=subject, new_password=new_password)

#     # Verify that the password was changed by attempting to authenticate with the new password
#     credentials = PasswordCredentials(username=subject, password=new_password)
#     identity = ldap_provider.authenticate(credentials=credentials)

#     assert isinstance(identity, Identity)
#     assert identity.subject == subject
