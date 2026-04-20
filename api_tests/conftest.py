import json
import os

os.environ['FLASK_ENV'] = 'production'

from pathlib import Path

import pytest

try:
    from alpha_test_api._app import app
except ImportError:
    raise Exception(
        'test api not found, please run test_pre_process.sh & pip install api/'
    )

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(autouse=True, scope='session')
def flask_app():
    resources_yaml = (
        PROJECT_ROOT / 'tests' / 'openapi' / 'specification' / 'openapi.yaml'
    )
    api_yaml = (
        PROJECT_ROOT / 'api' / 'alpha_test_api' / 'openapi' / 'openapi.yaml'
    )
    if not os.environ.get('CI', None):
        if os.stat(resources_yaml).st_mtime > os.stat(api_yaml).st_mtime:
            raise ValueError(
                f'{resources_yaml} is updated since the last '
                f'generation of the test API. Please re-run the '
                f'test_pre_process.sh to reflect these changes'
            )

    yield app.app


@pytest.fixture(autouse=True, scope='session')
def client(flask_app):
    flask_app.testing = True
    yield flask_app.test_client()


@pytest.fixture
def get(client):
    def _get(path, obj=None):
        if obj is not None:
            return client.get(f'{path}/{obj}')
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
def auth_path():
    return '/auth/login'


@pytest.fixture
def credentials():
    return {
        'username': 'admin',
        'password': 'admin123',
    }
