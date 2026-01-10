def test_password_credentials(password_credentials):
    assert password_credentials.username == "testuser"
    assert password_credentials.password == "securepassword123"


def test_password_credentials_to_dict(password_credentials):
    assert password_credentials.to_dict() == {
        "username": "testuser",
        "password": "securepassword123",
    }


def test_password_credentials_str_and_repr(password_credentials):
    assert str(password_credentials) == "testuser"
    assert repr(password_credentials) == (
        "PasswordCredentials(username='testuser', password=***)"
    )
