def test_token(token):
    assert token.value == "abcdef123456"
    assert token.token_type == "Bearer"
