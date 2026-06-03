from datetime import datetime, timedelta, timezone
import json

import pytest

from alpha.providers.models.token import Token
from alpha.repositories.refresh.database_refresh_repository import (
    DatabaseRefreshRepository,
)

from alpha.repositories.refresh.file_refresh_repository import (
    FileRefreshRepository,
)
from alpha.repositories.refresh.memory_refresh_repository import (
    MemoryRefreshRepository,
)
from tests.fixtures.fake_database_connector import FakeSqlAlchemyConnector


@pytest.fixture
def token():
    return "fake_token_value"


@pytest.fixture
def subject():
    return "fake_subject_value"


@pytest.fixture
def database_refresh_repository(token):
    fake_connector = FakeSqlAlchemyConnector(obj=token)
    return DatabaseRefreshRepository(database_connector=fake_connector)


@pytest.fixture
def database_refresh_repository_no_token():
    fake_connector = FakeSqlAlchemyConnector(obj=None)
    return DatabaseRefreshRepository(database_connector=fake_connector)


@pytest.fixture
def fake_refresh_token(token, subject) -> Token:
    return Token(
        value=token,
        token_type="Refresh",
        subject=subject,
        expires_at=datetime.now(tz=timezone.utc) + timedelta(seconds=3600),
    )


@pytest.fixture
def refresh_tokens_file_content(
    token,
    fake_refresh_token,
):
    return {
        token: fake_refresh_token.to_dict(),
    }


@pytest.fixture
def refresh_token_storage_file_path(tmp_path):
    return tmp_path / "refresh_tokens.json"


@pytest.fixture
def refresh_token_storage_file(
    refresh_token_storage_file_path, refresh_tokens_file_content
):
    with open(refresh_token_storage_file_path, "w") as f:
        f.write(json.dumps(refresh_tokens_file_content))
    return refresh_token_storage_file_path


@pytest.fixture
def file_refresh_repository(token, refresh_token_storage_file):
    return FileRefreshRepository(file_path=refresh_token_storage_file)


@pytest.fixture
def memory_refresh_repository(token, fake_refresh_token):
    repo = MemoryRefreshRepository()
    repo._refresh_tokens = {token: fake_refresh_token}
    return repo
