def test_user_permissions_management(
    auth_path,
    client,
    admin_credentials,
    user_credentials,
    test_user,
    test_group,
):
    # Log in with user user_credentials to get the token
    response = client.post(auth_path, json=user_credentials)
    assert response.status_code == 401

    # Log in with admin credentials to get the token
    response = client.post(auth_path, json=admin_credentials)
    assert response.status_code == 201
    admin_token = response.json["data"]

    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Use the admin_token to get the user details, add the user, and update
    # it
    users_response = client.get(
        f"/users/{user_credentials.username}", headers=admin_headers
    )
    assert users_response.status_code == 404

    new_user_response = client.post(
        "/users", json=test_user, headers=admin_headers
    )
    print(f"{new_user_response.json=}")
    assert new_user_response.status_code == 201

    # Update the user to add it to the test group
    update_obj = new_user_response.json.get("data", {})
    user_id = update_obj.get("id")
    update_obj["groups"] = [test_group["name"]]
    for attr in [
        "id",
        "created_by",
        "modified_by",
        "created_at",
        "modified_at",
    ]:
        if attr in update_obj:
            del update_obj[attr]

    updated_user_response = client.put(
        f"/users/{user_id}",
        json=update_obj,
        headers=admin_headers,
    )
    assert updated_user_response.status_code == 200

    # Log in with user user_credentials to get the token
    response = client.post(auth_path, json=user_credentials)
    assert response.status_code == 201
    token = response.json["data"]

    headers = {"Authorization": f"Bearer {token}"}

    # Use the token to access a protected endpoint
    users_response = client.get("/permissions", headers=headers)
    assert users_response.status_code == 403

    # Add a group which corresponds to the group added to the user, and verify
    # that the user is now part of the group.
    group_response = client.post(
        "/groups", json=test_group, headers=admin_headers
    )
    assert group_response.status_code == 201

    # Update the group to add a permission
    update_group_obj = group_response.json.get("data", {})
    group_id = update_group_obj.get("id")
    update_group_obj["permissions"] = ["TEST_PERMISSION"]
    for attr in [
        "id",
        "created_by",
        "modified_by",
        "created_at",
        "modified_at",
    ]:
        if attr in update_group_obj:
            del update_group_obj[attr]
    updated_group_response = client.put(
        f"/groups/{group_id}",
        json=update_group_obj,
        headers=admin_headers,
    )
    print(f"{updated_group_response.json=}")
    assert updated_group_response.status_code == 200

    # Log in again with user credentials to get the new token
    response = client.post(auth_path, json=user_credentials)
    assert response.status_code == 201
    token = response.json["data"]

    headers = {"Authorization": f"Bearer {token}"}

    # Use the token to access a protected endpoint. Now that the user is part
    # of the group, it should have access to the endpoint.
    users_response = client.get("/permissions", headers=headers)
    print(f"{users_response.json=}")
    assert users_response.status_code == 200
