import pytest
from fastapi.testclient import TestClient
from pytest_httpserver import HTTPServer
from common_code.config import get_settings
from common_code.logger.logger import get_logger
from common_code.storage.service import StorageService
from main import app
import time


@pytest.fixture(name="storage")
def storage_fixture():
    settings = get_settings()
    logger = get_logger(settings)

    storage = StorageService(logger=logger)

    yield storage


@pytest.fixture(name="client")
def client_fixture(reachable_engine_instance: HTTPServer):
    def get_settings_override():
        settings = get_settings()
        settings.engine_url = reachable_engine_instance.url_for("")
        settings.engine_announce_retries = 2
        settings.engine_announce_retry_delay = 1
        settings.max_tasks = 2

        return settings

    app.dependency_overrides[get_settings] = get_settings_override

    # client = TestClient(app)
    # yield client

    with TestClient(app) as client:
        # We wait for the app to announce itself to the engine (ugly)
        time.sleep(5)
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="reachable_engine_instance")
def reachable_engine_instance_fixture(httpserver: HTTPServer):
    httpserver.expect_request("/services").respond_with_json({}, status=200)

    yield httpserver

    httpserver.clear()


@pytest.fixture(name="unreachable_engine_instance")
def unreachable_engine_instance_fixture(httpserver: HTTPServer):
    httpserver.expect_request("/services").respond_with_json({}, status=500)

    yield httpserver

    httpserver.clear()


@pytest.fixture(name="app_with_reachable_engine_instance")
def app_with_reachable_engine_instance(reachable_engine_instance: HTTPServer):
    def get_settings_override():
        settings = get_settings()
        settings.engine_url = reachable_engine_instance.url_for("")
        settings.engine_announce_retries = 2
        settings.engine_announce_retry_delay = 1
        settings.max_tasks = 2

        return settings

    # I don't understand why, in this specific case, I need to call the `get_settings_override` function
    # for this to work where elsewhere I can pass the function as it is...
    app.dependency_overrides[get_settings] = get_settings_override()

    yield app
    app.dependency_overrides.clear()


@pytest.fixture(name="app_with_unreachable_engine_instance")
def app_with_unreachable_engine_instance(unreachable_engine_instance: HTTPServer):
    def get_settings_override():
        settings = get_settings()
        settings.engine_url = unreachable_engine_instance.url_for("")
        settings.engine_announce_retries = 2
        settings.engine_announce_retry_delay = 1
        settings.max_tasks = 2

        return settings

    # I don't understand why, in this specific case, I need to call the `get_settings_override` function
    # for this to work where elsewhere I can pass the function as it is...
    app.dependency_overrides[get_settings] = get_settings_override()

    yield app
    app.dependency_overrides.clear()


def test_announce_to_reachable_engine(caplog: pytest.LogCaptureFixture, app_with_reachable_engine_instance):
    with TestClient(app_with_reachable_engine_instance):
        # We wait for the app to announce itself to the engine (ugly)
        time.sleep(5)

        # We look for `WARNING` messages in the logs to check if the service wasn't
        # able to announce itself to the engine.
        #
        # This is not a good way to test the app as any other warnings will make the test
        # passes.
        warning_logs_found = False
        for record in caplog.records:
            if record.levelname == "WARNING":
                warning_logs_found = True
                break

        assert not warning_logs_found


def test_announce_to_unreachable_engine(caplog: pytest.LogCaptureFixture, app_with_unreachable_engine_instance):
    with TestClient(app_with_unreachable_engine_instance):
        # We wait for the app to announce itself to the engine (ugly)
        time.sleep(5)

        # We look for `WARNING` messages in the logs to check if the service wasn't
        # able to announce itself to the engine.
        #
        # This is not a good way to test the app as any other warnings will make the test
        # passes.
        warning_logs_found = False
        for record in caplog.records:
            if record.levelname == "WARNING":
                warning_logs_found = True
                break

        assert warning_logs_found


def test_status(client: TestClient):
    status_response = client.get("/status")

    # Check the output
    assert status_response.status_code == 200
