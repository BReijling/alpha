import pytest

from alpha.domain.models.group import GroupWithObjects
from alpha.domain.models.permission import Permission
from alpha.domain.models.user import UserWithObjects
from alpha.exceptions import BadRequestException, NotFoundException
from alpha.infra.models.json_patch import JsonPatch
from alpha.services.user_lifecycle_management import UserLifecycleManagement


def test_user_lifecycle_management_service_user_lifecycle(
    user_lifecycle_management_service: UserLifecycleManagement,
    alt_test_user,
    updated_alt_test_user,
    alt_test_user_patch,
):
    service = user_lifecycle_management_service
    users = service.get_users()
    assert isinstance(users, list)
    assert len(users) == 0

    new_user = service.add_user(alt_test_user)
    assert new_user.username == alt_test_user.username
    assert new_user.display_name == alt_test_user.display_name
    assert new_user.groups == []
    assert new_user.permissions == []

    users = service.get_users(user_ids=[new_user.id])
    assert len(users) == 1
    assert users[0].username == alt_test_user.username
    assert users[0].display_name == alt_test_user.display_name

    user = service.get_user(new_user.id)
    assert user.username == alt_test_user.username
    assert user.display_name == alt_test_user.display_name
    assert user.id == new_user.id
    assert user.password is not alt_test_user.password

    updated_user = service.update_user(new_user.id, updated_alt_test_user)
    assert updated_user.display_name == updated_alt_test_user.display_name
    assert updated_user.username == updated_alt_test_user.username
    assert updated_user.id == new_user.id

    user = service.get_user(new_user.id)
    assert user.display_name == updated_alt_test_user.display_name
    assert user.username == updated_alt_test_user.username
    assert user.id == new_user.id

    patched_user = service.patch_user(new_user.id, alt_test_user_patch)
    assert patched_user.display_name == alt_test_user_patch.patch[0]["value"]
    assert patched_user.username == alt_test_user_patch.patch[1]["value"]

    user = service.get_user(new_user.id)
    assert user.display_name == alt_test_user_patch.patch[0]["value"]
    assert user.username == alt_test_user_patch.patch[1]["value"]
    assert user.id == new_user.id

    service.remove_user(new_user.id)
    users = service.get_users()
    assert len(users) == 0


def test_user_lifecycle_management_service_group_lifecycle(
    user_lifecycle_management_service: UserLifecycleManagement,
    alt_test_group,
    updated_alt_test_group,
    alt_test_group_patch,
):
    service = user_lifecycle_management_service
    groups = service.get_groups()
    assert isinstance(groups, list)
    assert len(groups) == 0

    new_group = service.add_group(alt_test_group)
    assert new_group.name == alt_test_group.name
    assert new_group.description == alt_test_group.description
    assert new_group.permissions == []

    groups = service.get_groups(group_ids=[new_group.id])
    assert len(groups) == 1
    assert groups[0].name == alt_test_group.name
    assert groups[0].description == alt_test_group.description

    group = service.get_group(new_group.id)
    assert group.name == alt_test_group.name
    assert group.description == alt_test_group.description
    assert group.id == new_group.id

    updated_group = service.update_group(new_group.id, updated_alt_test_group)
    assert updated_group.name == updated_alt_test_group.name
    assert updated_group.description == updated_alt_test_group.description
    assert updated_group.id == new_group.id

    group = service.get_group(new_group.id)
    assert group.name == updated_alt_test_group.name
    assert group.description == updated_alt_test_group.description
    assert group.id == new_group.id

    patched_group = service.patch_group(new_group.id, alt_test_group_patch)
    assert patched_group.name == alt_test_group_patch.patch[0]["value"]
    assert patched_group.description == alt_test_group_patch.patch[1]["value"]

    group = service.get_group(new_group.id)
    assert group.name == alt_test_group_patch.patch[0]["value"]
    assert group.description == alt_test_group_patch.patch[1]["value"]
    assert group.id == new_group.id

    service.remove_group(new_group.id)
    groups = service.get_groups()
    assert len(groups) == 0


def test_user_lifecycle_management_service_permission_lifecycle(
    user_lifecycle_management_service: UserLifecycleManagement,
    alt_test_permission,
    updated_alt_test_permission,
):
    service = user_lifecycle_management_service
    permissions = service.get_permissions()
    assert isinstance(permissions, list)
    assert len(permissions) == 0

    new_permission = service.add_permission(alt_test_permission)
    assert new_permission.name == alt_test_permission.name
    assert new_permission.description == alt_test_permission.description

    permissions = service.get_permissions(permission_ids=[new_permission.id])
    assert len(permissions) == 1
    assert permissions[0].name == alt_test_permission.name
    assert permissions[0].description == alt_test_permission.description

    permission = service.get_permission(new_permission.id)
    assert permission.name == alt_test_permission.name
    assert permission.description == alt_test_permission.description
    assert permission.id == new_permission.id

    updated_permission = service.update_permission(
        new_permission.id, updated_alt_test_permission
    )
    assert updated_permission.name == updated_alt_test_permission.name
    assert (
        updated_permission.description
        == updated_alt_test_permission.description
    )
    assert updated_permission.id == new_permission.id

    permission = service.get_permission(new_permission.id)
    assert permission.name == updated_alt_test_permission.name
    assert permission.description == updated_alt_test_permission.description
    assert permission.id == new_permission.id

    service.remove_permission(new_permission.id)
    permissions = service.get_permissions()
    assert len(permissions) == 0


def test_user_lifecycle_management_service_relations(
    user_lifecycle_management_service: UserLifecycleManagement,
    alt_test_user,
    alt_test_group,
    alt_test_permission,
):
    service = user_lifecycle_management_service

    # Initially, there should be no users, groups, or permissions in the service.
    assert service.get_users() == []
    assert service.get_groups() == []
    assert service.get_permissions() == []

    # Add a new user, group, and permission to the service.
    new_user = service.add_user(alt_test_user)
    new_group = service.add_group(alt_test_group)
    new_permission = service.add_permission(alt_test_permission)

    # Create a patch to add the new permission to the user and group.
    add_permission_patch = JsonPatch(
        [
            {
                "op": "add",
                "path": "/permissions",
                "value": str(new_permission.id),
            }
        ]
    )

    # Patch the user to add the new permission.
    patched_user = service.patch_user(
        new_user.id,
        add_permission_patch,
    )
    assert patched_user.permissions[0].id == new_permission.id

    # Patch the group to add the new permission.
    patched_group = service.patch_group(
        new_group.id,
        add_permission_patch,
    )
    assert patched_group.permissions[0].id == new_permission.id

    # Create a patch to add the new group to the user.
    add_group_patch = JsonPatch(
        [
            {
                "op": "add",
                "path": "/groups",
                "value": str(new_group.id),
            }
        ]
    )
    patched_user = service.patch_user(
        new_user.id,
        add_group_patch,
    )
    # Verify that the user now has the new group and retains the permission.
    assert patched_user.groups[0].id == new_group.id
    assert patched_user.permissions[0].id == new_permission.id

    users = service.get_users()
    assert len(users) == 1
    assert users[0].id == new_user.id
    assert users[0].groups[0].id == new_group.id
    assert users[0].permissions[0].id == new_permission.id

    # Remove the permission and verify that the related permission is removed
    # from the user and group.
    service.remove_permission(new_permission.id)
    users = service.get_users()
    assert users[0].permissions == []
    assert users[0].groups[0].permissions == []

    # Add the permission back and verify that it can be added to the user and
    # group again.
    new_permission = service.add_permission(alt_test_permission)
    add_permission_patch = JsonPatch(
        [
            {
                "op": "add",
                "path": "/permissions",
                "value": str(new_permission.id),
            }
        ]
    )
    patched_user = service.patch_user(
        new_user.id,
        add_permission_patch,
    )
    assert patched_user.permissions[0].id == new_permission.id

    patched_group = service.patch_group(
        new_group.id,
        add_permission_patch,
    )
    assert patched_group.permissions[0].id == new_permission.id

    with pytest.raises(NotFoundException):
        service.patch_user(
            new_user.id,
            JsonPatch(
                [
                    {
                        "op": "add",
                        "path": "/permissions",
                        "value": "name",
                    }
                ]
            ),
        )
    with pytest.raises(BadRequestException):
        service.patch_user(
            new_user.id,
            JsonPatch(
                [
                    {
                        "op": "replace",
                        "path": "/permissions",
                        "value": str(new_permission.id),
                    }
                ]
            ),
        )

    # Verify that the user and group now have the new permission.
    users = service.get_users()
    assert users[0].permissions[0].id == new_permission.id
    assert users[0].groups[0].permissions[0].id == new_permission.id

    # Use update to modify to remove the permission from the user and group.
    updated_group = service.update_group(
        new_group.id,
        GroupWithObjects(
            name=new_group.name,
            description=new_group.description,
            permissions=[],
        ),
    )
    assert updated_group.permissions == []

    updated_group = service.update_group(
        new_group.id,
        GroupWithObjects(
            name=new_group.name,
            description=new_group.description,
            permissions=[Permission(name=new_permission.name)],
        ),
    )
    assert updated_group.permissions[0].id == new_permission.id

    updated_user = service.update_user(
        new_user.id,
        UserWithObjects(
            username=new_user.username,
            display_name=new_user.display_name,
            groups=[GroupWithObjects(name=new_group.name)],
            permissions=[Permission(name=new_permission.name)],
        ),
    )
    assert updated_user.permissions[0].id == new_permission.id
    assert updated_user.groups[0].id == new_group.id

    with pytest.raises(NotFoundException):
        service.update_group(
            new_group.id,
            GroupWithObjects(
                name=new_group.name,
                description=new_group.description,
                permissions=[Permission(name="name")],
            ),
        )
    service.patch_user(
        new_user.id,
        JsonPatch(
            [
                {
                    "op": "remove",
                    "path": "/permissions",
                    "value": str(new_permission.id),
                }
            ]
        ),
    )

    with pytest.raises(BadRequestException):
        service.patch_user(
            new_user.id,
            JsonPatch(
                [
                    {
                        "op": "replace",
                        "path": "/groups",
                        "value": str(new_group.id),
                    }
                ]
            ),
        )

    service.patch_user(
        new_user.id,
        JsonPatch(
            [
                {
                    "op": "remove",
                    "path": "/groups",
                    "value": str(new_group.id),
                }
            ]
        ),
    )
