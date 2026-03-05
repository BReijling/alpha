import pytest

from alpha.services.models.cookie import Cookie


@pytest.fixture
def cookie():
    return Cookie(
        key="test_cookie", value="test_value", max_age=3600, path="/"
    )
