"""Contains the PermissionLifecycleMixin class."""

from typing import TYPE_CHECKING
from uuid import UUID

from alpha.infra.models.search_filter import SearchFilter, Operator
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.mixins.user_group_helper import UserGroupHelperMixin
from alpha.providers.models.identity import Identity

if TYPE_CHECKING:
    from alpha.domain.models.permission import Permission
else:
    Permission = object


class PermissionLifecycleMixin(UserGroupHelperMixin):
    """Mixin class managing the lifecycle of Permission objects."""

    uow: UnitOfWork
    _permissions_repository_name: str = "permissions"
    _permission_model: type[Permission] = Permission

    def add_permission(
        self, permission: Permission, identity: Identity | None = None
    ) -> Permission:
        """Add a new permission object to the repository.

        Parameters
        ----------
        permission
            New permission object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `created_by` attribute of the permission will be
            updated with the username from the identity.

        Returns
        -------
        Permission
            Created permission object
        """
        permission = self._permission_model(**permission.to_dict())

        if identity:
            permission.created_by = identity.username

        with self.uow:
            repository = self._get_permissions_repository()
            permission = repository.add(permission, raise_if_exists=True)
            self.uow.commit()
            return permission

    def get_permission(self, permission_id: str | int | UUID) -> Permission:
        """Get a permission object by id from the repository.

        Parameters
        ----------
        permission_id
            The id of the permission object

        Returns
        -------
        Permission
            Permission object which corresponds to the id

        Raises
        ------
        NotFoundException
            When the object is not found in the repository
        """
        with self.uow:
            permission = self._get_permission_by_id(
                permission_id=permission_id
            )

            return permission

    def get_permissions(
        self, permission_ids: list[str] | None = None
    ) -> list[Permission]:
        """Get all permission objects from the repository.

        Parameters
        ----------
        permission_ids
            An optional list of permission ids to filter on

        Returns
        -------
        list[Permission]
            A collection of all the permission objects
        """
        filters: list[SearchFilter] = []

        if permission_ids:
            filters.append(
                SearchFilter(field="id", op=Operator.IN, value=permission_ids)
            )

        with self.uow:
            repository = self._get_permissions_repository()
            permissions = repository.select(filters=filters)

            return permissions

    def remove_permission(self, permission_id: str | int | UUID) -> None:
        """Remove a permission object from the repository.

        Parameters
        ----------
        permission_id
            The id of the permission object
        """
        with self.uow:
            repository = self._get_permissions_repository()

            permission = self._get_permission_by_id(
                permission_id=permission_id
            )

            repository.remove(permission)
            self.uow.commit()

    def update_permission(
        self,
        permission_id: str | int | UUID,
        permission: Permission,
        identity: Identity | None = None,
    ) -> Permission:
        """Update an existing permission object in the repository.

        Parameters
        ----------
        permission
            Permission object with changes
        permission_id
            The id of the permission object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `modified_by` attribute of the permission will be
            updated with the username from the identity.

        Returns
        -------
        Permission
            Updated permission object
        """
        permission = self._permission_model(**permission.to_dict())

        with self.uow:
            original_permission = self._get_permission_by_id(
                permission_id=permission_id
            )

            updated_permission = original_permission.update(permission)
            if identity:
                updated_permission.modified_by = identity.username
            self.uow.commit()

        return updated_permission
