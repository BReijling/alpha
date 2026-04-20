def test_authentication(auth_path, credentials, client):
    response = client.post(auth_path, json=credentials)
    assert response.status_code == 201

    token = response.json['data']

    # Verify user identity with the token
    response = client.get(
        '/auth/verify', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    identity = response.json['data']

    assert identity['username'] == credentials['username']

    # Refresh the token
    refresh_response = client.get(
        '/auth/refresh', headers={'Authorization': f'Bearer {token}'}
    )
    assert refresh_response.status_code == 201
    new_token = refresh_response.json['data']

    assert (
        len(new_token.split('.')) == 3
    ), 'Token should be a JWT with three parts separated by dots'


def test_user_management(auth_path, credentials, client):
    # First, log in to get the token
    response = client.post(auth_path, json=credentials)
    assert response.status_code == 201
    token = response.json['data']

    # Use the token to access a protected endpoint
    users_response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )
    assert users_response.status_code == 200

    data = users_response.json['data']

    assert False
