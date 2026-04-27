"""Contains the GroupLifecycleMixin class"""

from uuid import UUID

from alpha.domain.models.group import Group
from alpha.exceptions import NotFoundException
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.providers.models.identity import Identity


class GroupLifecycleMixin:
    """Mixin class providing methods for managing the lifecycle of Group
    objects.
    """

    uow: UnitOfWork
    _groups_repository_name: str
    _group_model: type[Group]

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
        group = self._group_model(**group.to_dict())

        if identity:
            group.created_by = identity.username

        with self.uow:
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )
            group = groups.add(group, raise_if_exists=True)
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
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )
            group = groups.get_by_id(group_id)

            if not group:
                raise NotFoundException(
                    f"Group with id '{group_id}' is not found"
                )

            return group

    def get_groups(self) -> list[Group]:
        """Gets all group objects from the repository

        Returns
        -------
        list[Group]
            A collection of all the group objects
        """
        with self.uow:
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )
            result = groups.select()

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
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )

            groups.remove(group)
            self.uow.commit()

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
        group = self._group_model(**group.to_dict())

        with self.uow:
            groups: SqlRepository[Group] = getattr(
                self.uow, self._groups_repository_name
            )
            original_group = groups.get_by_id(group_id)

            if not original_group:
                raise NotFoundException(
                    f"Group with id '{group_id}' is not found"
                )

            updated_group = original_group.update(group)
            if identity:
                updated_group.modified_by = identity.username
            self.uow.commit()

        return updated_group
