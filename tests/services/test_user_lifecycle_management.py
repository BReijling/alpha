import pytest

from alpha.exceptions import BadRequestException, NotFoundException
from alpha.services.user_lifecycle_management import UserLifecycleManagement


def test_user_lifecycle_management_service_add_user(
    user_lifecycle_management_service: UserLifecycleManagement,
    test_user,
    test_user3,
    test_identity,
):
    added_user = user_lifecycle_management_service.add_user(
        test_user, test_identity
    )

    assert added_user.username == test_user.username
    assert added_user.created_by == test_identity.username

    with pytest.raises(BadRequestException):
        user_lifecycle_management_service.add_user(test_user3)


def test_user_lifecycle_management_service_alternative_username_attribute(
    user_lifecycle_management_service_alternative_username_attribute: UserLifecycleManagement,
    test_user,
):
    with pytest.raises(BadRequestException):
        user_lifecycle_management_service_alternative_username_attribute.add_user(
            test_user
        )


def test_user_lifecycle_management_service_get_user(
    user_lifecycle_management_service: UserLifecycleManagement, fake_uow
):
    user = user_lifecycle_management_service.get_user(2)

    assert user is not None
    assert user.id == 1

    fake_uow.users.objs = []  # Clear users to simulate user not found

    with pytest.raises(NotFoundException):
        user_lifecycle_management_service.get_user(999)


def test_user_lifecycle_management_service_get_users(
    user_lifecycle_management_service: UserLifecycleManagement,
):
    users = user_lifecycle_management_service.get_users()

    assert isinstance(users, list)
    assert len(users) == 1
    assert users[0].id == 1


def test_user_lifecycle_management_service_remove_user(
    user_lifecycle_management_service: UserLifecycleManagement, fake_uow
):
    assert len(fake_uow.users.objs) == 1

    user_lifecycle_management_service.remove_user(1)

    assert len(fake_uow.users.objs) == 0

    with pytest.raises(NotFoundException):
        user_lifecycle_management_service.remove_user(999)


def test_user_lifecycle_management_service_update_user(
    user_lifecycle_management_service: UserLifecycleManagement,
    test_identity,
    test_user,
):
    updated_user = user_lifecycle_management_service.update_user(
        1, test_user, test_identity
    )

    assert updated_user.modified_by == test_identity.username


def test_user_lifecycle_management_service_add_group(
    user_lifecycle_management_service: UserLifecycleManagement,
    test_group,
    test_identity,
):
    added_group = user_lifecycle_management_service.add_group(
        test_group, test_identity
    )

    assert added_group.name == test_group.name
    assert added_group.created_by == test_identity.username


def test_user_lifecycle_management_service_get_group(
    user_lifecycle_management_service: UserLifecycleManagement, fake_uow
):
    group = user_lifecycle_management_service.get_group(0)

    assert group is not None
    assert group.id == 1

    fake_uow.groups.objs = []  # Clear groups to simulate group not found

    with pytest.raises(NotFoundException):
        user_lifecycle_management_service.get_group(999)


def test_user_lifecycle_management_service_get_groups(
    user_lifecycle_management_service: UserLifecycleManagement,
):
    groups = user_lifecycle_management_service.get_groups()

    assert isinstance(groups, list)
    assert len(groups) == 3
    assert groups[0].id == 1


def test_user_lifecycle_management_service_remove_group(
    user_lifecycle_management_service: UserLifecycleManagement, fake_uow
):
    assert len(fake_uow.groups.objs) == 3

    user_lifecycle_management_service.remove_group(0)

    assert len(fake_uow.groups.objs) == 2

    fake_uow.groups.objs = []  # Clear groups to simulate group not found

    with pytest.raises(NotFoundException):
        user_lifecycle_management_service.remove_group(999)


def test_user_lifecycle_management_service_update_group(
    user_lifecycle_management_service: UserLifecycleManagement,
    test_identity,
    test_group,
):
    updated_group = user_lifecycle_management_service.update_group(
        0, test_group, test_identity
    )

    assert updated_group.modified_by == test_identity.username
