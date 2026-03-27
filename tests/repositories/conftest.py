import httpx
import pytest
import requests
import threading
from flask import Flask, request
from werkzeug.serving import make_server

from alpha.infra.models.json_patch import JsonPatch
from alpha.repositories.rest_api_repository import RestApiRepository
from alpha.repositories.sql_alchemy_repository import SqlAlchemyRepository
from tests.fixtures._domain_models import TestModel
from tests.fixtures.fake_session import FakeSqlAlchemySession


@pytest.fixture
def fake_sql_alchemy_session():
    return FakeSqlAlchemySession("test_value")


@pytest.fixture
def sql_alchemy_repository(fake_sql_alchemy_session) -> SqlAlchemyRepository:
    return SqlAlchemyRepository(
        session=fake_sql_alchemy_session, default_model="Model"
    )


@pytest.fixture(autouse=True, scope="package")
def flask_app() -> Flask:
    app = Flask(__name__)

    @app.route("/objects/<id>", methods=["GET"])
    def test_single_object(id):
        return {"status": "ok", "data": {"value": id}}, 200

    @app.route("/parents/<parent_id>/objects/<id>", methods=["GET"])
    def test_single_object_by_parent(parent_id, id):
        return {"status": "ok", "data": {"value": f"{parent_id}_{id}"}}, 200

    @app.route("/objects", methods=["GET"])
    def test_multiple_objects():
        return {
            "status": "ok",
            "data": [{"value": "abc"}, {"value": "def"}],
        }, 200

    @app.route("/objects", methods=["POST"])
    def test_endpoint_post():
        obj = request.json
        return {"status": "ok", "data": obj}, 201

    @app.route("/objects/<id>", methods=["PUT"])
    def test_endpoint_put(id):
        obj = request.json
        return {"status": "ok", "data": obj}, 200

    @app.route("/objects/<id>", methods=["PATCH"])
    def test_endpoint_patch(id):
        patch = request.json
        return {"status": "ok", "data": {"value": patch[0]["value"]}}, 200

    @app.route("/objects/<id>", methods=["DELETE"])
    def test_endpoint_delete(id):
        obj = request.json
        return {"status": "ok", "data": obj}, 204

    @app.route("/status/<status_code>", methods=["GET"])
    def test_status(status_code):
        return {"status": "ok", "data": {"value": status_code}}, int(
            status_code
        )

    yield app


@pytest.fixture(scope="package")
def test_api_server(flask_app):
    server = make_server("127.0.0.1", 0, flask_app)
    host = f"http://127.0.0.1:{server.server_port}"
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    yield host

    server.shutdown()
    server_thread.join()


@pytest.fixture
def rest_api_repository(test_api_server) -> RestApiRepository:
    repository = RestApiRepository(
        host=test_api_server,
        endpoint="/objects",
        default_model=TestModel,
        response_data_attribute="data",
        model_factory_method_name="factory",
    )
    session = repository._session
    yield repository
    session.close()


@pytest.fixture
def rest_api_repository_no_model(test_api_server) -> RestApiRepository:
    session = requests.sessions.Session()
    repository = RestApiRepository(
        session=session,
        host=test_api_server,
        endpoint="/objects",
    )
    yield repository
    session.close()


@pytest.fixture
def rest_api_repository_status(test_api_server) -> RestApiRepository:
    session = requests.sessions.Session()
    repository = RestApiRepository(
        session=session,
        host=test_api_server,
        endpoint="/status",
    )
    yield repository
    session.close()


@pytest.fixture
def rest_api_repository_httpx(test_api_server) -> RestApiRepository:
    session = httpx.Client()
    repository = RestApiRepository(
        session=session,
        host=test_api_server,
        endpoint="/objects",
        default_model=TestModel,
        response_data_attribute="data",
        model_factory_method_name="factory",
    )
    yield repository
    session.close()


@pytest.fixture
def rest_api_repository_no_serialization(test_api_server) -> RestApiRepository:
    session = requests.sessions.Session()
    repository = RestApiRepository(
        session=session,
        host=test_api_server,
        endpoint="/objects",
        default_model=TestModel,
        response_data_attribute="data",
        model_factory_method_name="factory",
        model_serialization_method_name="test",
        serialize=True,
    )
    yield repository
    session.close()


@pytest.fixture
def rest_api_repository_for_build_url() -> RestApiRepository:
    repository = RestApiRepository(
        session=None,
        host="localhost:5000",
        scheme="http",
        base_path="api/v1",
        endpoint="objects",
    )
    return repository


@pytest.fixture
def test_model() -> TestModel:
    return TestModel(value="def")


@pytest.fixture
def json_patch():
    return JsonPatch(
        [{"op": "replace", "path": "/value", "value": "patched_value"}]
    )
