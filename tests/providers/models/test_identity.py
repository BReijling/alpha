from datetime import datetime, timezone

from alpha.providers.models.identity import (
    DEFAULT_AD_MAPPINGS,
    DEFAULT_LDAP_MAPPINGS,
    Identity,
)


def test_identity(identity):
    assert identity.subject == "user123"
    assert identity.username == "testuser"
    assert identity.email == "testuser@example.com"
    assert identity.display_name == "Test User"
    assert identity.groups == ["group1", "group2"]
    assert identity.permissions == ["read", "write"]
    assert identity.claims == {"role": "admin"}
    assert isinstance(identity.issued_at, datetime)
    assert identity.issued_at.tzinfo == timezone.utc
    assert isinstance(identity.expires_at, datetime)
    assert identity.expires_at.tzinfo == timezone.utc
    assert identity.role == "SUPERUSER"
    assert identity.audience is None
    assert identity.admin is False
    assert identity.pretend_identity is None


def test_identity_from_ldap_dict(ldap_dict):
    identity = Identity.from_ldap_dict(
        ldap_dict, mappings=DEFAULT_LDAP_MAPPINGS
    )

    assert identity.subject == "ldap_user"
    assert identity.username == "ldap_user"
    assert identity.email == "ldap_user@example.com"
    assert identity.display_name is None
    assert identity.groups == ["group1", "group2"]
    assert identity.permissions == []
    assert identity.claims != {}
    assert isinstance(identity.issued_at, datetime)
    assert identity.issued_at.tzinfo == timezone.utc
    assert identity.expires_at is None
    assert identity.audience is None
    assert identity.admin is False
    assert identity.pretend_identity is None


def test_identity_from_ad_dict(ad_dict):
    identity = Identity.from_ldap_dict(ad_dict, mappings=DEFAULT_AD_MAPPINGS)

    assert identity.subject == "ad_user"
    assert identity.username == "ad_user"
    assert identity.email == "ad_user@example.com"
    assert identity.display_name == "Display AD User"
    assert identity.groups == ["group1", "group2", "group3, with, commas"]
    assert identity.permissions == []
    assert identity.claims != {}
    assert isinstance(identity.issued_at, datetime)
    assert identity.issued_at.tzinfo == timezone.utc
    assert identity.expires_at is None
    assert identity.audience is None
    assert identity.admin is False
    assert identity.pretend_identity is None


def test_identity_from_and_to_dict(identity):
    identity_dict = identity.to_dict()

    assert identity_dict["subject"] == "user123"
    assert identity_dict["username"] == "testuser"
    assert identity_dict["email"] == "testuser@example.com"
    assert identity_dict["display_name"] == "Test User"
    assert identity_dict["groups"] == ["group1", "group2"]
    assert identity_dict["permissions"] == ["read", "write"]
    assert identity_dict["claims"] == {"role": "admin"}
    assert identity_dict["issued_at"] == identity.issued_at.isoformat()
    assert identity_dict["expires_at"] == identity.expires_at.isoformat()
    assert identity_dict["audience"] is None
    assert identity_dict["admin"] is False
    assert identity_dict["pretend_identity"] is None

    new_identity = Identity.from_dict(identity_dict)

    assert new_identity == identity


def test_identity_str_and_repr(identity):
    assert str(identity) == "user123"

    repr_str = repr(identity)

    assert "Identity(" in repr_str
    assert "subject='user123'" in repr_str
    assert "username='testuser'" in repr_str
    assert "email='testuser@example.com'" in repr_str
    assert "display_name='Test User'" in repr_str
    assert "groups=['group1', 'group2']" in repr_str
    assert "permissions=['read', 'write']" in repr_str
    assert "claims={'role': 'admin'}" in repr_str
    assert "issued_at=" in repr_str
    assert "expires_at=" in repr_str
    assert "audience=None" in repr_str
    assert "admin=False" in repr_str
    assert "pretend_identity=None" in repr_str
