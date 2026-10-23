"""Contains the UserLifecycleMixin class"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID

from alpha.exceptions import BadRequestException, ForbiddenException
from alpha.factories.password_factory import PasswordFactory
from alpha.infra.models.json_patch import JsonPatch, PatchDict
from alpha.infra.models.search_filter import Operator, SearchFilter
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.mixins.user_group_helper import UserGroupHelperMixin
from alpha.providers.models.identity import Identity

if TYPE_CHECKING:
    from alpha.domain.models.user import User
    from alpha.domain.models.permission import Permission
    from alpha.domain.models.group import Group
else:
    User = Any
    Permission = Any
    Group = Any


class UserLifecycleMixin(UserGroupHelperMixin):
    """Mixin class providing methods for managing the lifecycle of User
    objects.
    """

    uow: UnitOfWork
    _users_repository_name: str = "users"
    _user_model: type[User] = User
    _password_support: bool = True
    _password_factory: PasswordFactory
    _user_username_attribute: str = "username"
    _user_password_attribute: str = "password"

    def add_user(self, user: User, identity: Identity | None = None) -> User:
        """Adds a new user object to the repository

        Parameters
        ----------
        user
            New user object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `created_by` attribute of the user will be updated
            with the username from the identity.

        Returns
        -------
        User
            Created user object
        """
        user = self._user_model.from_dict(user.to_dict())

        if not hasattr(user, self._user_username_attribute) or not getattr(
            user, self._user_username_attribute
        ):
            raise BadRequestException("Username of User attribute is empty")

        if self._password_support:
            if not hasattr(user, self._user_password_attribute) or not getattr(
                user, self._user_password_attribute
            ):
                raise BadRequestException(
                    "Password of User attribute is empty"
                )

            setattr(
                user,
                self._user_password_attribute,
                self._password_factory.hash_password(
                    password=getattr(user, self._user_password_attribute)
                ),
            )

        if identity:
            user.created_by = identity.username

        with self.uow:
            repository = self._get_users_repository()
            user = repository.add(user, raise_if_exists=True)
            self.uow.commit()
            return user

    def get_user(self, user_id: str | int | UUID) -> User:
        """Get an user object by id from the repository

        Parameters
        ----------
        user_id
            The id of the user object

        Returns
        -------
        User
            User object which corresponds to the id

        Raises
        ------
        NotFoundException
            When the object is not found in the repository
        """
        with self.uow:
            user = self._get_user_by_id(user_id)

            return user

    def get_users(
        self, user_ids: list[str | int | UUID] | None = None
    ) -> list[User]:
        """Gets all user objects from the repository, optionally filtered by user IDs

        Parameters
        ----------
        user_ids
            An optional list of user ids to filter on


        Returns
        -------
        list[User]
            A collection of all the user objects
        """
        filters: list[SearchFilter] = []

        if user_ids:
            filters.append(
                SearchFilter(field="id", op=Operator.IN, value=user_ids)
            )

        with self.uow:
            repository = self._get_users_repository()
            result = repository.select(filters=filters)

            return result

    def remove_user(self, user_id: str | int | UUID) -> None:
        """Removes an user object from the repository

        Parameters
        ----------
        user_id
            The id of the user object
        """
        with self.uow:
            repository = self._get_users_repository()
            user = self._get_user_by_id(user_id)

            repository.remove(user)
            self.uow.commit()

    def patch_user(
        self,
        user_id: str,
        json_patch: JsonPatch,
        identity: Identity | None = None,
    ) -> User:
        """Patch an existing user object in the repository

        Parameters
        ----------
        user_id
            The id of the user object
        json_patch
            The JSON patch to apply to the user object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `modified_by` attribute of the user will be updated
            with the username from the identity.

        Returns
        -------
        User
            The patched user object
        """
        with self.uow:
            user = self._get_user_by_id(user_id)
            for patch in cast(list[PatchDict], json_patch):
                path = str(patch["path"]).strip("/")

                if path == "groups" and "groups" not in user.__patch_fields__:
                    self._patch_groups(obj=user, patch=patch)
                elif (
                    path == "permissions"
                    and "permissions" not in user.__patch_fields__
                ):
                    self._patch_permissions(obj=user, patch=patch)
                elif path == "id":
                    raise ForbiddenException(
                        "The id parameter cannot be patched"
                    )
                else:
                    user.patch(patch)

            if identity:
                user.modified_by = identity.username
            user.modified_at = datetime.now(tz=UTC)
            self.uow.commit()
            return user

    def update_user(
        self,
        user_id: str | int | UUID,
        user: User,
        identity: Identity | None = None,
    ) -> User:
        """Updates an existing user object in the repository

        Parameters
        ----------
        user
            User object with changes
        user_id
            The id of the user object
        identity
            The identity of the user making the changes, by default None. If
            provided, the `modified_by` attribute of the user will be updated
            with the username from the identity.

        Returns
        -------
        User
            Updated user object
        """
        user = self._user_model.from_dict(user.to_dict())
        update_fields = user.__update_fields__

        with self.uow:
            original_user = self._get_user_by_id(user_id)
            updated_user = original_user.update(user)

            if "permissions" not in update_fields:
                updated_user.permissions = []
                for permission in cast(list[Permission], user.permissions):
                    _permission = self._get_permission_by_id_or_name(
                        str(permission.name)
                    )
                    updated_user.add_permission(_permission)  # type: ignore
            if "groups" not in update_fields:
                updated_user.groups = []
                for group in cast(list[Group], user.groups):
                    _group = self._get_group_by_id_or_name(str(group.name))
                    updated_user.add_group(_group)  # type: ignore

            if identity:
                updated_user.modified_by = identity.username
            self.uow.commit()

            return updated_user
