from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any, Self, Sequence, TYPE_CHECKING
from datetime import datetime, timezone


if TYPE_CHECKING:
    from alpha.domain.models.user import User

DEFAULT_LDAP_MAPPINGS = {
    "subject": "uid",
    "username": "uid",
    "email": "mail",
    "display_name": "cn",
    "groups": "memberOf",
    "permissions": "permissions",
}

DEFAULT_AD_MAPPINGS = {
    "subject": "sAMAccountName",
    "username": "sAMAccountName",
    "email": "mail",
    "display_name": "displayName",
    "groups": "memberOf",
    "permissions": "permissions",
}


@dataclass
class Identity:
    """Represents the authenticated identity of a user within the application.

    This class is typically populated from an external identity provider (e.g.
    LDAP, OIDC, SAML) and used throughout the system for authorization,
    auditing, and personalization.

    Attributes
    ----------
    subject
        Globally unique identifier for the user (e.g. LDAP uid, OIDC sub).
    username
        Short, human-friendly login name, if available.
    email
        Primary email address of the user, if available.
    display_name
        Human-readable name to show in the UI, if available.
    groups
        Collection of group names or roles the user is a member of.
    permissions
        Specific permissions or scopes granted to the user.
    claims
        Arbitrary key/value pairs about the user, as provided by the identity
        provider. This can include standard token claims (e.g. issuer, scopes,
        tenant, custom attributes) or raw LDAP attributes. It is a flexible
        extension point for carrying additional identity metadata without
        changing the core Identity fields.
    issued_at
        Timestamp when this identity was issued / loaded.
    expires_at
        Optional timestamp when this identity should be considered invalid
        (e.g. token expiry, session timeout).
    audience
        Optional list of logical audiences for which this identity is valid. In
        token-based authentication this usually maps to the `aud` claim
        (e.g. OAuth2/OIDC client IDs or services). It allows the application to
        verify that an identity is meant to be used by this specific
        application or API.
    role
        Optional high-level role assigned to the user (e.g. "user", "admin",
        "manager"). This is distinct from groups and permissions, and is often
        used for coarse-grained access control or UI personalization.
    admin
        Indicates whether the user has elevated administrative privileges.
    pretend_identity
        When set, indicates that this identity is impersonating another subject
        (e.g. admin acting on behalf of a user).
    """

    subject: str  # unique user id (sub / dn / uid)
    username: str | None
    email: str | None
    display_name: str | None
    groups: Sequence[str]
    permissions: Sequence[str]
    claims: Mapping[str, Any]
    issued_at: datetime
    expires_at: datetime | None = None
    role: str | None = None
    audience: Sequence[str] | None = None
    admin: bool = False
    pretend_identity: Self | None = None

    @classmethod
    def from_ldap_dict(
        cls,
        entry: Mapping[str, Any],
        mappings: Mapping[str, str] = DEFAULT_LDAP_MAPPINGS,
        populate_groups: bool = True,
        populate_permissions: bool = False,
        populate_claims: bool = True,
    ) -> "Identity":
        """Instantiate an Identity from an LDAP entry dictionary.

        Parameters
        ----------
        entry
            LDAP entry dictionary containing user attributes.
        mappings, optional
            Attribute mappings from LDAP fields to Identity fields, by default
            DEFAULT_LDAP_MAPPINGS
        populate_groups, optional
            Whether to extract groups from the LDAP entry, by default True
        populate_permissions, optional
            Whether to extract permissions from the LDAP entry, by default
            False
        populate_claims, optional
            Whether to populate the claims dictionary from the LDAP entry, by
            default True

        Returns
        -------
            An Identity instance populated with data from the LDAP entry.
        """
        username = cls._get_key(entry, mappings["username"])
        if not username:
            username = cls._get_key(entry, mappings["subject"])

        return cls(
            subject=cls._get_key(entry, mappings["subject"], ""),
            username=username,
            email=cls._get_key(entry, mappings["email"]),
            display_name=cls._get_key(entry, mappings["display_name"]),
            groups=cls._extract_groups(entry) if populate_groups else [],
            permissions=(
                cls._get_key(
                    entry,
                    mappings["permissions"],
                    default=[],
                    return_type=list,
                )
                if populate_permissions
                else []
            ),
            claims=(
                cls._remove_password_from_claims(entry)
                if populate_claims
                else {}
            ),
            issued_at=datetime.now(tz=timezone.utc),
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Identity":
        """Instantiate an Identity from a generic dictionary.

        Parameters
        ----------
        data
            Dictionary containing identity attributes.

        Returns
        -------
            An Identity instance populated with data from the dictionary.
        """
        issued_at = data.get("issued_at", datetime.now(tz=timezone.utc))
        if isinstance(issued_at, str):
            issued_at = datetime.fromisoformat(issued_at)
        expires_at = data.get("expires_at", None)
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)

        return cls(
            subject=data.get("subject", ""),
            username=data.get("username", None),
            email=data.get("email", None),
            display_name=data.get("display_name", None),
            groups=data.get("groups", []),
            permissions=data.get("permissions", []),
            claims=data.get("claims", {}),
            issued_at=issued_at,
            expires_at=expires_at,
            audience=data.get("audience", None),
            role=data.get("role", None),
            admin=data.get("admin", False),
            pretend_identity=(
                Identity.from_dict(data.get("pretend_identity", {}))
                if data.get("pretend_identity")
                else None
            ),
        )

    def update_from_user(self, user: User) -> None:
        """Update the Identity instance with data from a User instance.

        Parameters
        ----------
        user
            User object to update from.
        """
        self.username = user.username
        self.email = user.email
        self.display_name = user.display_name
        for permission in user.permissions or []:
            if permission not in self.permissions:
                self.permissions.append(permission)  # type: ignore
        for group in user.groups or []:
            if group not in self.groups:
                self.groups.append(group)  # type: ignore
        self.role = user.role
        self.admin = user.admin

    def __str__(self) -> str:
        return self.subject

    def __repr__(self) -> str:
        return (
            "Identity("
            f"subject={self.subject!r}, "
            f"username={self.username!r}, "
            f"email={self.email!r}, "
            f"display_name={self.display_name!r}, "
            f"groups={self.groups!r}, "
            f"permissions={self.permissions!r}, "
            f"claims={self.claims!r}, "
            f"issued_at={self.issued_at!r}, "
            f"expires_at={self.expires_at!r}, "
            f"audience={self.audience!r}, "
            f"role={self.role!r}, "
            f"admin={self.admin!r}, "
            f"pretend_identity={self.pretend_identity!r}"
            ")"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the Identity instance to a dictionary.

        Returns
        -------
            A dictionary representation of the Identity instance.
        """
        return {
            "subject": self.subject,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "groups": self.groups,
            "permissions": self.permissions,
            "claims": self.claims,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": (
                self.expires_at.isoformat() if self.expires_at else None
            ),
            "audience": self.audience,
            "role": self.role,
            "admin": self.admin,
            "pretend_identity": (
                self.pretend_identity.to_dict()
                if self.pretend_identity
                else None
            ),
        }

    @staticmethod
    def _get_key(
        obj: Mapping[str, Any],
        key: str,
        default: Any = None,
        return_type: type = str,
    ) -> Any:
        """Helper method to get a key from a dictionary with type casting.

        Parameters
        ----------
        obj
            Source dictionary.
        key
            Key to retrieve.
        default, optional
            Default value to return if the key is not found, by default None
        return_type, optional
            Expected return type for the value, by default str

        Returns
        -------
            The value associated with the key, cast to the specified type. If
            the key is not found, returns the default value.
        """
        value: str | list[Any] | None = obj.get(key, default)
        if value is not None and not isinstance(value, return_type):
            if isinstance(value, list) and len(value) > 0:
                value = value[0]
            try:
                value = return_type(value)
            except (ValueError, TypeError):
                value = default
        return value

    @staticmethod
    def _remove_password_from_claims(
        claims: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Return a copy of the Identity with password-related claims removed.

        This method creates a new Identity instance with sensitive password
        information removed from the claims dictionary to enhance security.

        Parameters
        ----------
        claims
            Original claims dictionary.

        Returns
        -------
            A new Identity instance without password-related claims.
        """
        filtered_claims = {
            k: v for k, v in claims.items() if "password" not in k.lower()
        }
        return filtered_claims

    @staticmethod
    def _extract_groups(
        entry: Mapping[str, Any],
    ) -> list[str]:
        """Extract group names from the LDAP entry's memberOf attribute.

        Parameters
        ----------
        entry
            LDAP entry dictionary containing user attributes.

        Returns
        -------
            A list of group names the user is a member of.
        """
        groups: list[str] = []
        for group in entry.get("memberOf", []):
            items = group.split(",")
            for item in items:
                if item.startswith("CN=") or item.startswith("cn="):
                    groups.append(item[3:])
                    break
        return groups
