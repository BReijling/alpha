from typing import Any
from alpha.providers.models.identity import Identity
from alpha.exceptions import InsufficientPermissionsException


def verify_identity(
    identity: Identity | dict[str, Any],
    roles: list[str] | None = None,
    groups: list[str] | None = None,
    permissions: list[str] | None = None,
) -> None:
    """Verify an Identity object for required roles, groups, and permissions.

    Parameters
    ----------
    identity
        The identity to verify, either as an Identity object or a dictionary.
    roles
        The roles to verify against the identity.
    groups
        The groups to verify against the identity.
    permissions
        The permissions to verify against the identity.

    Returns
    -------
        A verified Identity object.

    Raises
    ------
        InsufficientPermissionsException
            If the provided identity is does not meet the required criteria,
            and had insufficient permissions.
    """
    if isinstance(identity, Identity):
        identity = identity.to_dict()

    identity_subject = identity.get("subject")
    identity_role = identity.get("role")
    identity_permissions = identity.get("permissions")
    identity_groups = identity.get("groups")

    # Verify if identity role is present in required roles
    if roles and identity_role not in roles:
        raise InsufficientPermissionsException(
            f"Role \'{identity_role}\' of \'{identity_subject}\' is not "
            f"sufficient. Required roles: {roles}"
        )

    # Verify if identity groups intersect with required groups
    if groups and not set(identity_groups).intersection(set(groups)):
        raise InsufficientPermissionsException(
            f"Groups \'{identity_groups}\' of \'{identity_subject}\' do not "
            f"intersect with required groups: {groups}"
        )

    # Verify if identity permissions include all required permissions
    if permissions and not set(permissions).issubset(
        set(identity_permissions)
    ):
        raise InsufficientPermissionsException(
            f"Permissions \'{identity_permissions}\' of \'{identity_subject}\'"
            f" do not include required permissions: {permissions}"
        )
