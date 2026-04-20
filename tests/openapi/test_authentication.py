def test_authentication_flow(auth_path, admin_credentials, client):
    response = client.post(auth_path, json=admin_credentials)
    assert response.status_code == 201
    token = response.json['data']

    headers = {'Authorization': f'Bearer {token}'}

    assert (
        len(token.split('.')) == 3
    ), 'Token should be a JWT with three parts separated by dots'

    # Verify user identity with the token
    response = client.get('/auth/verify', headers=headers)
    assert response.status_code == 200
    identity = response.json['data']

    assert identity['username'] == admin_credentials.username

    # Refresh the token
    refresh_response = client.get('/auth/refresh', headers=headers)
    assert refresh_response.status_code == 201
    new_token = refresh_response.json['data']

    assert (
        len(new_token.split('.')) == 3
    ), 'Token should be a JWT with three parts separated by dots'

    # Logout
    logout_response = client.post('/auth/logout', headers=headers)
    assert logout_response.status_code == 204

    # Verify that the old refresh token is invalidated
    refresh_response = client.get('/auth/refresh', headers=headers)
    assert refresh_response.status_code == 401
