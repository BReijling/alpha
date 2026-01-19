"""OIDC identity providers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Sequence, cast

from alpha import exceptions
from alpha.infra.connectors.oidc_connector import (
    OIDCConnector,
)
from alpha.interfaces.token_factory import TokenFactory
from alpha.mixins.jwt_provider import JWTProviderMixin
from alpha.providers.models.credentials import PasswordCredentials
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token

DEFAULT_OIDC_MAPPINGS: dict[str, str | Sequence[str]] = {
    "subject": "sub",
    "username": "preferred_username",
    "email": "email",
    "display_name": "name",
    "groups": "groups",
    "permissions": "scope",
}

DEFAULT_KEYCLOAK_MAPPINGS: dict[str, str | Sequence[str]] = {
    "subject": "sub",
    "username": "preferred_username",
    "email": "email",
    "display_name": "name",
    "groups": "groups",
    "permissions": [
        "realm_access.roles",
        "resource_access.roles",
        "scope",
    ],
}


class OIDCProvider(JWTProviderMixin):
    """OIDC identity provider.

    Parameters
    ----------
    connector
        Connector to use for OIDC operations.
    token_factory, optional
        Factory used to issue/validate local tokens.
    claim_mappings, optional
        Mapping of OIDC claims to Identity fields.
    populate_groups, optional
        Whether to populate group memberships on the Identity.
    populate_permissions, optional
        Whether to populate permissions on the Identity.
    populate_claims, optional
        Whether to include raw claims on the Identity.
    change_password_supported, optional
        Whether this provider supports changing passwords.
    """

    protocol = "oidc"
    _token_factory: TokenFactory | None = None

    def __init__(
        self,
        connector: OIDCConnector,
        token_factory: TokenFactory | None = None,
        claim_mappings: Mapping[str, str | Sequence[str]] | None = None,
        populate_groups: bool = True,
        populate_permissions: bool = False,
        populate_claims: bool = False,
        change_password_supported: bool = False,
    ) -> None:
        self._connector = connector
        self._token_factory = token_factory
        self._claim_mappings = (
            dict(claim_mappings) if claim_mappings else DEFAULT_OIDC_MAPPINGS
        )
        self._populate_groups = populate_groups
        self._populate_permissions = populate_permissions
        self._populate_claims = populate_claims
        self._change_password_supported = change_password_supported

    def authenticate(self, credentials: PasswordCredentials) -> Identity:
        """Authenticate a user using OIDC password flow.

        Parameters
        ----------
        credentials
            User credentials.

        Returns
        -------
        Identity
            Authenticated user identity.
        """
        token_data = self._connector.request_password_token(
            username=credentials.username,
            password=credentials.password,
        )

        access_token = token_data.get("access_token")
        if not access_token:
            raise exceptions.InvalidCredentialsException(
                "OIDC token response did not include access_token"
            )

        claims = {}
        if self._connector.userinfo_url:
            claims = self._connector.get_userinfo(access_token)

        merged_claims = {**token_data, **claims}
        return self._convert_claims_to_identity(merged_claims)

    def get_user(self, subject: str) -> Identity:
        """Retrieve a user by subject using an admin lookup.

        Parameters
        ----------
        subject
            User subject identifier.

        Returns
        -------
        Identity
            Retrieved user identity.
        """
        if not self._connector.user_lookup_url_template:
            raise exceptions.NotSupportedException(
                "User lookup is not configured for this provider"
            )

        claims = self._connector.get_user_by_subject(subject)
        return self._convert_claims_to_identity(claims)

    def change_password(
        self, credentials: PasswordCredentials, new_password: str
    ) -> None:
        """Change user password (if supported).

        Parameters
        ----------
        credentials
            Current user credentials.
        new_password
            New password to set.
        """
        if not self._change_password_supported:
            raise exceptions.NotSupportedException(
                "Change password operation is not supported by this provider"
            )
        raise exceptions.NotSupportedException(
            "Change password is not implemented for OIDC providers"
        )

    def validate(self, token: Token) -> Identity:
        """Validate a token using token factory or introspection.

        Parameters
        ----------
        token
            Token to validate.

        Returns
        -------
        Identity
            Validated user identity.
        """
        if self._token_factory:
            return super().validate(token)

        if not self._connector.introspection_url:
            raise exceptions.NotSupportedException(
                "Token introspection is not configured for this provider"
            )

        claims = self._connector.introspect_token(token.value)
        if not claims.get("active", False):
            raise exceptions.InvalidTokenException("Token is not active")

        return self._convert_claims_to_identity(claims)

    def _convert_claims_to_identity(
        self, claims: Mapping[str, Any]
    ) -> Identity:
        """Convert OIDC claims to an Identity.

        Parameters
        ----------
        claims
            OIDC claims to convert.

        Returns
        -------
            Converted Identity object.

        Raises
        ------
        exceptions.IdentityError
            Raised if the claims do not include a required subject.
        """
        subject = self._get_claim(claims, "subject")
        if not subject:
            raise exceptions.IdentityError(
                "OIDC claims did not include a subject"
            )

        username = self._get_claim(claims, "username")
        if not username:
            username = subject

        issued_at = datetime.now(tz=timezone.utc)

        groups = (
            self._extract_sequence(self._get_claim(claims, "groups"))
            if self._populate_groups
            else []
        )

        permissions = (
            self._extract_permissions(claims)
            if self._populate_permissions
            else []
        )

        audience = self._extract_audience(claims)

        identity = Identity(
            subject=str(subject),
            username=username,
            email=self._get_claim(claims, "email"),
            display_name=self._get_claim(claims, "display_name"),
            groups=groups,
            permissions=permissions,
            claims=dict(claims) if self._populate_claims else {},
            issued_at=issued_at,
            audience=audience,
            role=self._get_claim(claims, "role"),
            admin=bool(self._get_claim(claims, "admin", False)),
        )
        return identity

    def _get_claim(
        self,
        claims: Mapping[str, Any],
        field: str,
        default: Any | None = None,
    ) -> Any:
        """Get a claim value by field name, using mappings if configured.

        Parameters
        ----------
        claims
            OIDC claims to retrieve the value from.
        field
            Name of the claim field to retrieve.
        default, optional
            Default value to return if the claim is not found, by default None.
        Returns
        -------
            Value of the claim field, or the default if not found.
        """
        mapping = self._claim_mappings.get(field)
        if mapping is None:
            return claims.get(field, default)

        for path in self._ensure_sequence(mapping):
            value = self._get_claim_by_path(claims, path)
            if value is not None:
                return value
        return default

    @staticmethod
    def _ensure_sequence(value: str | Sequence[str]) -> Sequence[str]:
        """Ensure the value is a sequence of strings.

        Parameters
        ----------
        value
            Value to ensure as a sequence of strings.

        Returns
        -------
            Sequence of strings.
        """
        if isinstance(value, str):
            return [value]
        return value

    @staticmethod
    def _get_claim_by_path(claims: Mapping[str, Any], path: str) -> Any:
        """Get a claim value by a dot-separated path.

        Parameters
        ----------
        claims
            OIDC claims to retrieve the value from.
        path
            Dot-separated path to the claim value.

        Returns
        -------
            Value of the claim at the specified path, or None if not found.
        """
        current: Any = claims
        for segment in path.split("."):
            if not isinstance(current, Mapping):
                return None
            current = cast(Mapping[str, Any], current).get(segment)
        return current

    @staticmethod
    def _extract_sequence(value: Any) -> list[str]:
        """Extract a sequence of strings from the given value.

        Parameters
        ----------
        value
            Value to extract the sequence from.

        Returns
        -------
            Sequence of strings.
        """
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, Sequence):
            return [str(item) for item in cast(Sequence[Any], value)]
        return [str(value)]

    def _extract_permissions(self, claims: Mapping[str, Any]) -> list[str]:
        """Extract permissions from the given claims.

        Parameters
        ----------
        claims
            OIDC claims to retrieve the permissions from.

        Returns
        -------
            Sequence of strings.
        """
        raw = self._get_claim(claims, "permissions")
        if raw is None:
            raw = claims.get("scope")
        if isinstance(raw, str):
            return [value for value in raw.split() if value]
        if isinstance(raw, Sequence):
            return [str(item) for item in cast(Sequence[Any], raw)]
        return []

    @staticmethod
    def _extract_audience(claims: Mapping[str, Any]) -> list[str] | None:
        """Extract audience from the given claims.

        Parameters
        ----------
        claims
            OIDC claims to retrieve the audience from.

        Returns
        -------
            Sequence of strings, or None if not found.
        """
        aud = claims.get("aud")
        if aud is None:
            return None
        if isinstance(aud, str):
            return [aud]
        if isinstance(aud, Sequence):
            return [str(item) for item in cast(Sequence[Any], aud)]
        return [str(aud)]


class KeyCloakProvider(OIDCProvider):
    """Keycloak identity provider based on OIDC.

    Parameters
    ----------
    connector
            Connector to use for OIDC operations.
    token_factory, optional
            Factory used to issue/validate local tokens.
    claim_mappings, optional
            Mapping of OIDC claims to Identity fields.
    populate_groups, optional
            Whether to populate group memberships on the Identity.
    populate_permissions, optional
            Whether to populate permissions on the Identity.
    populate_claims, optional
            Whether to include raw claims on the Identity.
    change_password_supported, optional
            Whether this provider supports changing passwords.
    """

    protocol = "oidc"

    def __init__(
        self,
        connector: OIDCConnector,
        token_factory: TokenFactory | None = None,
        claim_mappings: Mapping[str, str | Sequence[str]] | None = None,
        populate_groups: bool = True,
        populate_permissions: bool = False,
        populate_claims: bool = False,
        change_password_supported: bool = False,
    ) -> None:

        super().__init__(
            connector=connector,
            token_factory=token_factory,
            claim_mappings=claim_mappings or DEFAULT_KEYCLOAK_MAPPINGS,
            populate_groups=populate_groups,
            populate_permissions=populate_permissions,
            populate_claims=populate_claims,
            change_password_supported=change_password_supported,
        )
