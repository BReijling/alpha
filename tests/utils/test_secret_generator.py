from alpha.utils.secret_generator import generate_secret


def test_generate_secret():
    secret = generate_secret()
    assert isinstance(secret, str)
    assert len(secret) == 32
    assert secret.isupper()

    short_secret = generate_secret(16)
    assert len(short_secret) == 16
    assert short_secret != generate_secret(16)
