import json
import os
import subprocess
from typing import Any, Generator

from alpha.infra.databases.sql_alchemy import SqlAlchemyDatabase
from alpha.providers.models.credentials import PasswordCredentials
from alpha.utils.openapi_test.orm import TestMapper

os.environ["FLASK_ENV"] = "production"

from pathlib import Path

import pytest

TEST_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = TEST_ROOT.parent


def _run_test_pre_process() -> None:
    script_path = PROJECT_ROOT / "test_pre_process.sh"
    if not script_path.exists():
        raise FileNotFoundError(f"Missing pre-process script: {script_path}")

    result = subprocess.run(
        ["sh", str(script_path)],
        cwd=str(PROJECT_ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Failed to run test_pre_process.sh before openapi tests.\n"
            f"stdout:\n{result.stdout}\n\n"
            f"stderr:\n{result.stderr}"
        )


@pytest.fixture(autouse=True, scope="session")
def flask_app():
    resources_yaml = TEST_ROOT / "openapi" / "specification" / "openapi.yaml"
    api_yaml = (
        PROJECT_ROOT / "api" / "alpha_test_api" / "openapi" / "openapi.yaml"
    )

    if (
        not api_yaml.exists()
        or os.stat(resources_yaml).st_mtime > os.stat(api_yaml).st_mtime
    ):
        _run_test_pre_process()

    try:
        import sys

        sys.path.insert(0, str(PROJECT_ROOT / "api"))
        from alpha_test_api._app import app
    except ImportError as exc:
        raise Exception(
            "test api not found after running test_pre_process.sh"
        ) from exc

    yield app.app


@pytest.fixture(autouse=True, scope="session")
def client(flask_app):
    flask_app.testing = True
    yield flask_app.test_client()


@pytest.fixture
def get(client):
    def _get(path, obj=None):
        if obj is not None:
            return client.get(f"{path}/{obj}")
        return client.get(path)

    return _get


@pytest.fixture
def post(client):
    def _post(path, body=None, data=None):
        return client.post(path, json=body, data=data)

    return _post


@pytest.fixture
def parse_response_json():
    return json.loads


@pytest.fixture
def pet_dict():
    return {
        "name": "Pluto",
        "pet_type": "DOG",
        "date_of_birth": "2000-01-01",
        "good_boy": True,
    }


@pytest.fixture
def bad_pet_dict():
    return {
        "name": "Lassie",
        "pet_type": "DOG",
        "date_of_birth": "2000-01-01",
        "good_boy": False,
    }


@pytest.fixture
def cat_dict():
    return {
        "name": "Garfield",
        "pet_type": "CAT",
        "date_of_birth": "2000-01-01",
        "good_boy": True,
    }


@pytest.fixture
def invalid_pet_dict():
    return {
        "name": "Clifford",
        "pet_type": "DOG",
        "date_of_birth": "2002-01-01",
        "good_boy": True,
        "weight": -12.9,
    }


@pytest.fixture
def auth_path():
    return "/auth/login"


@pytest.fixture
def admin_credentials() -> PasswordCredentials:
    return PasswordCredentials(username="admin", password="admin123")


@pytest.fixture
def user_credentials() -> PasswordCredentials:
    return PasswordCredentials(
        username="test_user", password="test_password123"
    )


@pytest.fixture
def test_user(user_credentials) -> dict[str, Any]:
    return dict(
        username=user_credentials.username,
        password=user_credentials.password,
        groups=["test_group"],
    )


@pytest.fixture(scope="session", autouse=True)
def psql_database() -> Generator[SqlAlchemyDatabase, None, None]:
    db = SqlAlchemyDatabase(
        host=os.getenv("TEST_PSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("TEST_PSQL_PORT", "5432")),
        username=os.getenv("TEST_PSQL_USERNAME", "postgres"),
        password=os.getenv("TEST_PSQL_PASSWORD", "postgres"),
        db_name=os.getenv("TEST_PSQL_DATABASE", "postgres"),
        db_type="postgresql",
        create_schema=False,
        create_tables=False,
        mapper=TestMapper,
    )
    yield db
    db.drop_tables(TestMapper.metadata)
