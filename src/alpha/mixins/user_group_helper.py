from typing import TYPE_CHECKING, cast
from uuid import UUID

from alpha.exceptions import (
    BadRequestException,
    NotFoundException,
)
from alpha.infra.models.json_patch import PatchDict
from alpha.interfaces.sql_repository import SqlRepository
from alpha.interfaces.unit_of_work import UnitOfWork

if TYPE_CHECKING:
    from alpha.domain.models.group import Group
    from alpha.domain.models.permission import Permission
    from alpha.domain.models.user import User
else:
    Group = object
    Permission = object
    User = object


class UserGroupHelperMixin:
    uow: UnitOfWork
    _users_repository_name: str = "users"
    _groups_repository_name: str = "groups"
    _permissions_repository_name: str = "permissions"
    _user_model: type[User] = User
    _group_model: type[Group] = Group
    _permission_model: type[Permission] = Permission

    def _patch_groups(self, obj: User, patch: PatchDict) -> None:
        """Patch the groups attribute of a User instance.

        This method should be called within the context of a unit of work to
        ensure a database session is active and changes are persisted.

        Parameters
        ----------
        obj
            A User instance.
        patch
            An object containing the patch parameters.

        Raises
        ------
        AlreadyExistsException
            When a group is already associated with the object.
        NotFoundException
            When a group specified in the patch is not associated with the
            object.
        NotFoundException
            If the group specified in the patch is not found.
        BadRequestException
            When using an unsupported operation value.
        """
        op, _, value = self._verify_patch(patch=patch)

        group = self._get_group_by_id_or_name(value)

        if op == "add":
            obj.add_group(group)  # type: ignore
        elif op == "remove":
            obj.remove_group(group)  # type: ignore
        else:
            raise BadRequestException(
                f"Using an unsupported operation value: '{op}'. Only 'add' "
                "and 'remove' are supported."
            )

    def _patch_permissions(
        self,
        obj: User | Group,
        patch: PatchDict,
    ) -> None:
        """Patch the permissions attribute of a Group or User instance.

        Parameters
        ----------
        obj
            A Group or User instance.
        patch
            An object containing the patch parameters.

        Raises
        ------
        AlreadyExistsException
            When a permission is already associated with the object.
        NotFoundException
            When a permission specified in the patch is not associated with the
            object.
        NotFoundException
            If the permission specified in the patch is not found.
        BadRequestException
            When using an unsupported operation value.
        """
        op, _, value = self._verify_patch(patch=patch)

        permission = self._get_permission_by_id_or_name(value)

        if op == "add":
            obj.add_permission(permission)  # type: ignore
        elif op == "remove":
            obj.remove_permission(permission)  # type: ignore
        else:
            raise BadRequestException(
                f"Using an unsupported operation value: '{op}'. Only 'add' "
                "and 'remove' are supported."
            )

    def _get_users_repository(
        self,
    ) -> SqlRepository[User]:
        """Retrieve the users repository from the unit of work.

        Returns
        -------
        SqlRepository[User]
            The users repository
        """
        try:
            return getattr(self.uow, self._users_repository_name)
        except AttributeError:
            raise NotFoundException(
                f"Users repository '{self._users_repository_name}'"
                " is not found in the unit of work"
            )

    def _get_user_by_id(
        self,
        user_id: str | int | UUID,
    ) -> User:
        """Retrieve a user by its ID from the specified repository.

        Parameters
        ----------
        user_id
            The ID of the user to retrieve

        Returns
        -------
        User
            The user object if found

        Raises
        ------
        NotFoundException
            If the user with the specified ID is not found
        """
        repository = self._get_users_repository()
        user = repository.get_by_id(user_id)

        if not user:
            raise NotFoundException(f"User with id '{user_id}' is not found")

        return user

    def _get_groups_repository(
        self,
    ) -> SqlRepository[Group]:
        """Retrieve the groups repository from the unit of work.

        Returns
        -------
        SqlRepository[Group]
            The groups repository
        """
        try:
            return getattr(self.uow, self._groups_repository_name)
        except AttributeError:
            raise NotFoundException(
                f"Groups repository '{self._groups_repository_name}'"
                " is not found in the unit of work"
            )

    def _get_group_by_id(
        self,
        group_id: str | int | UUID,
    ) -> Group:
        """Retrieve a group by its ID from the specified repository.

        Parameters
        ----------
        group_id
            The ID of the group to retrieve

        Returns
        -------
        Group
            The group object if found

        Raises
        ------
        NotFoundException
            If the group with the specified ID is not found
        """
        repository = self._get_groups_repository()
        group = repository.get_by_id(group_id)

        if not group:
            raise NotFoundException(f"Group with id '{group_id}' is not found")

        return group

    def _get_permission_by_name(self, name: str) -> Permission:
        """Retrieve a permission by its name from the specified repository.

        Parameters
        ----------
        name
            The name of the permission to retrieve

        Returns
        -------
        Permission
            The permission object if found

        Raises
        ------
        NotFoundException
            If the permission with the specified name is not found
        """
        repository = self._get_permissions_repository()
        permission = repository.get_one_or_none(attr="name", value=name)

        if not permission:
            raise NotFoundException(
                f"Permission with name '{name}' is not found"
            )

        return permission

    def _get_permission_by_id_or_name(
        self, identifier: str | UUID
    ) -> Permission:
        """Retrieve a permission by its ID or name from the specified
        repository.

        Parameters
        ----------
        identifier
            The ID or name of the permission to retrieve

        Returns
        -------
        Permission
            The permission object if found

        Raises
        ------
        NotFoundException
            If the permission with the specified ID or name is not found
        """
        repository = self._get_permissions_repository()
        permission = None
        if self._is_valid_uuid(identifier):
            permission = repository.get_by_id(identifier)

        if not permission:
            permission = repository.get_one_or_none(
                attr="name", value=identifier
            )

        if not permission:
            raise NotFoundException(
                f"Permission with id or name '{identifier}' is not found"
            )

        return permission

    def _get_group_by_name(self, name: str) -> Group:
        """Retrieve a group by its name from the specified repository.

        Parameters
        ----------
        name
            The name of the group to retrieve

        Returns
        -------
        Group
            The group object if found

        Raises
        ------
        NotFoundException
            If the group with the specified name is not found
        """
        repository = self._get_groups_repository()
        group = repository.get_one_or_none(attr="name", value=name)

        if not group:
            raise NotFoundException(f"Group with name '{name}' is not found")

        return group

    def _get_group_by_id_or_name(self, identifier: str | UUID) -> Group:
        """Retrieve a group by its ID or name from the specified repository.

        Parameters
        ----------
        identifier
            The ID or name of the group to retrieve

        Returns
        -------
        Group
            The group object if found

        Raises
        ------
        NotFoundException
            If the group with the specified ID or name is not found
        """
        repository = self._get_groups_repository()
        group = None
        if self._is_valid_uuid(identifier):
            group = repository.get_by_id(identifier)

        if not group:
            group = repository.get_one_or_none(attr="name", value=identifier)

        if not group:
            raise NotFoundException(
                f"Group with id or name '{identifier}' is not found"
            )

        return group

    def _get_permissions_repository(
        self,
    ) -> SqlRepository[Permission]:
        """Retrieve the permissions repository from the unit of work.

        Returns
        -------
        SqlRepository[Permission]
            The permissions repository
        """
        try:
            return getattr(self.uow, self._permissions_repository_name)
        except AttributeError:
            raise NotFoundException(
                f"Permissions repository '{self._permissions_repository_name}'"
                " is not found in the unit of work"
            )

    def _get_permission_by_id(
        self,
        permission_id: str | int | UUID,
    ) -> Permission:
        """Retrieve a permission by its ID from the specified repository.

        Parameters
        ----------
        permission_id
            The ID of the permission to retrieve

        Returns
        -------
        Permission
            The permission object if found

        Raises
        ------
        NotFoundException
            If the permission with the specified ID is not found
        """
        repository = self._get_permissions_repository()
        permission = repository.get_by_id(permission_id)

        if not permission:
            raise NotFoundException(
                f"Permission with id '{permission_id}' is not found"
            )

        return permission

    def _create_patch(self, op: str, path: str, value: str) -> dict[str, str]:
        """Create a patch object.

        Parameters
        ----------
        op
            The patch operation.
        path
            The patch path.
        value
            The patch value.

        Returns
        -------
        dict[str, str]
            A patch object
        """
        return {"op": op, "path": path, "value": value}

    def _verify_patch(self, patch: PatchDict) -> tuple[str, str, str]:
        """Verify the parameters of the patch object.

        All parameters are required and the operation parameter should be
        'add', 'remove' or 'replace'. Like RFC 6902, a 'remove' operation
        may leave out the value; it then becomes an empty string.

        Parameters
        ----------
        patch
            Patch object which contains the 'op', 'path' and 'value' keys.

        Returns
        -------
        tuple[str, str, str]
            The value for the 'op', 'path' and 'value' keys.

        Raises
        ------
        BadRequestException
            One or more parameters are None.
        BadRequestException
            When using an unsupported operation value.
        """
        op = cast(str, patch.get("op"))
        path = cast(str, patch.get("path"))
        value = cast(str, patch.get("value"))

        if op == "remove" and value is None:  # type: ignore
            value = ""

        if op is None or path is None or value is None:  # type: ignore
            raise BadRequestException(
                "Missing value in patch object. The 'op', 'path' and "
                "'value' are all required."
            )

        if op not in ["add", "remove", "replace"]:
            raise BadRequestException(
                f"Using an unsupported operation value: '{op}'. Only 'add' "
                "'remove' and 'replace' are supported."
            )

        return op, path, value

    def _is_valid_uuid(self, value: str | UUID) -> bool:
        """Check if the value contains a valid UUID.

        Parameters
        ----------
        value
            String or UUID to check

        Returns
        -------
        bool
            True if the value is a valid UUID, False if not.
        """
        if isinstance(value, UUID):
            return True
        try:
            UUID(value)
            return True
        except (ValueError, TypeError):
            return False
