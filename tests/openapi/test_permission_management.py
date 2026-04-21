def test_user_permissions_management(
    auth_path,
    client,
    admin_credentials,
    user_credentials,
    test_user,
):
    # Log in with user user_credentials to get the token
    response = client.post(auth_path, json=user_credentials)
    assert response.status_code == 401

    # Log in with admin credentials to get the token
    response = client.post(auth_path, json=admin_credentials)
    assert response.status_code == 201
    admin_token = response.json['data']

    admin_headers = {'Authorization': f'Bearer {admin_token}'}

    # Use the admin_token to get the user details, add the user, and update
    # it
    users_response = client.get(
        f'/users/{user_credentials.username}', headers=admin_headers
    )
    assert users_response.status_code == 404

    new_user_response = client.post(
        '/users', json=test_user, headers=admin_headers
    )
    assert new_user_response.status_code == 201

    # Log in with user user_credentials to get the token
    response = client.post(auth_path, json=user_credentials)
    assert response.status_code == 201
    token = response.json['data']

    headers = {'Authorization': f'Bearer {token}'}

    # Use the token to access a protected endpoint
    users_response = client.get('/permissions', headers=headers)
    assert users_response.status_code == 403

    # Add a group which corresponds to the group added to the user, and verify
    # that the user is now part of the group
    group = {
        "name": "test_group",
        "permissions": ["TEST_PERMISSION"],
        "description": "A test group",
    }
    group_response = client.post('/groups', json=group, headers=admin_headers)
    assert group_response.status_code == 201

    # Log in again with user credentials to get the new token
    response = client.post(auth_path, json=user_credentials)
    assert response.status_code == 201
    token = response.json['data']

    headers = {'Authorization': f'Bearer {token}'}

    # Use the token to access a protected endpoint
    users_response = client.get('/permissions', headers=headers)
    assert users_response.status_code == 200
