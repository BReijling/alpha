"""Contains the GroupLifecycleMixin class"""

from datetime import datetime, UTC
from typing import TYPE_CHECKING, cast
from uuid import UUID

from alpha.infra.models.json_patch import JsonPatch
from alpha.infra.models.search_filter import Operator, SearchFilter
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.mixins.user_group_helper import PATCH_TYPE, UserGroupHelperMixin
from alpha.providers.models.identity import Identity

if TYPE_CHECKING:
    from alpha.domain.models.group import Group
    from alpha.domain.models.permission import Permission
else:
    Group = object
    Permission = object


class GroupLifecycleMixin(UserGroupHelperMixin):
    """Mixin class providing methods for managing the lifecycle of Group
    objects.
    """

    uow: UnitOfWork
    _groups_repository_name: str = "groups"
    _group_model: type[Group] = Group

    def add_group(
        self, group: Group, identity: Identity | None = None
    ) -> Group:
        """Adds a new group object to the repository

        Parameters
        ----------
        group
            New group object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `created_by` attribute of the group will be updated
            with the username from the identity.

        Returns
        -------
        Group
            Created group object
        """
        group.permissions = []
        group = self._group_model.from_dict(group.to_dict())

        if identity:
            group.created_by = identity.username

        with self.uow:
            repository = self._get_groups_repository()
            group = repository.add(group, raise_if_exists=True)
            self.uow.commit()
            return group

    def get_group(self, group_id: str | int | UUID) -> Group:
        """Get a group object by id from the repository

        Parameters
        ----------
        group_id
            The id of the group object

        Returns
        -------
        Group
            Group object which corresponds to the id

        Raises
        ------
        NotFoundException
            When the object is not found in the repository
        """
        with self.uow:
            group = self._get_group_by_id(group_id=group_id)

            return group

    def get_groups(
        self, group_ids: list[str | int | UUID] | None = None
    ) -> list[Group]:
        """Gets all group objects from the repository

        Parameters
        ----------
        group_ids
            An optional list of group ids to filter on

        Returns
        -------
        list[Group]
            A collection of all the group objects
        """
        filters: list[SearchFilter] = []

        if group_ids:
            filters.append(
                SearchFilter(field="id", op=Operator.IN, value=group_ids)
            )

        with self.uow:
            repository = self._get_groups_repository()
            result = repository.select(filters=filters)

            return result

    def remove_group(self, group_id: str | int | UUID) -> None:
        """Removes a group object from the repository

        Parameters
        ----------
        group_id
            The id of the group object
        """
        group = self.get_group(group_id=group_id)
        with self.uow:
            repository = self._get_groups_repository()

            repository.remove(group)
            self.uow.commit()

    def patch_group(
        self,
        group_id: str,
        json_patch: JsonPatch,
        identity: Identity | None = None,
    ) -> Group:
        """Patch an existing group object in the repository

        Parameters
        ----------
        group_id
            The id of the group object
        json_patch
            The JSON patch to apply to the group object
        identity
            The identity of the group making the changes, by default None. If
            provided, the `modified_by` attribute of the group will be updated
            with the groupname from the identity.

        Returns
        -------
        Group
            The patched group object
        """
        with self.uow:
            group = self._get_group_by_id(group_id)
            for patch in cast(list[PATCH_TYPE], json_patch):
                path = str(patch["path"]).strip("/")

                if (
                    path == "permissions"
                    and "permissions" not in group.__patch_fields__
                ):
                    self._patch_permissions(obj=group, patch=patch)
                else:
                    group.patch(patch)

            if identity:
                group.modified_by = identity.username
            group.modified_at = datetime.now(tz=UTC)
            self.uow.commit()
            return group

    def update_group(
        self,
        group_id: str | int | UUID,
        group: Group,
        identity: Identity | None = None,
    ) -> Group:
        """Updates an existing group object in the repository

        Parameters
        ----------
        group
            Group object with changes
        group_id
            The id of the group object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `modified_by` attribute of the group will be updated
            with the username from the identity.

        Returns
        -------
        Group
            Updated group object
        """
        group = self._group_model.from_dict(group.to_dict())
        update_fields = group.__update_fields__

        with self.uow:
            original_group = self._get_group_by_id(group_id)
            updated_group = original_group.update(group)

            if "permissions" not in update_fields:
                updated_group.permissions = []
                for permission in cast(list[Permission], group.permissions):
                    perm = self._get_permission_by_id_or_name(
                        str(permission.name)
                    )
                    updated_group.add_permission(perm)

            if identity:
                updated_group.modified_by = identity.username
            self.uow.commit()

        return updated_group
