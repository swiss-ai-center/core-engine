# TODO: Fix this test
# import pytest
# from fastapi.testclient import TestClient
# from pytest_httpserver import HTTPServer
# from config import get_settings
# from logger.logger import get_logger
# from storage.service import StorageService
# from main import app
# import time
#
#
# @pytest.fixture(name="storage")
# def storage_fixture():
#     settings = get_settings()
#     logger = get_logger(settings)
#
#     storage = StorageService(logger=logger)
#
#     yield storage
#
#
# @pytest.fixture(name="client")
# def client_fixture(reachable_engine_instance: HTTPServer):
#     def get_settings_override():
#         settings = get_settings()
#         settings.engine_url = reachable_engine_instance.url_for("")
#         settings.engine_announce_retries = 2
#         settings.engine_announce_retry_delay = 1
#         settings.max_tasks = 2
#
#         return settings
#
#     app.dependency_overrides[get_settings] = get_settings_override
#
#     # client = TestClient(app)
#     # yield client
#
#     with TestClient(app) as client:
#         # We wait for the app to announce itself to the engine (ugly)
#         time.sleep(5)
#         yield client
#
#     app.dependency_overrides.clear()
#
#
# @pytest.fixture(name="reachable_engine_instance")
# def reachable_engine_instance_fixture(httpserver: HTTPServer):
#     httpserver.expect_request("/services").respond_with_json({}, status=200)
#
#     yield httpserver
#
#     httpserver.clear()
#
#
# service_task = {
#   "s3_access_key_id": "minio",
#   "s3_secret_access_key": "minio123",
#   "s3_region": "eu-central-2",
#   "s3_host": "http://localhost:9000",
#   "s3_bucket": "engine",
#   "task": {
#     "data_in": [],
#     "service_id": "00000000-0000-0000-0000-000000000000",
#     "pipeline_id": "00000000-0000-0000-0000-000000000000",
#     "id": "00000000-0000-0000-0000-000000000000"
#   }
# }
#

# @pytest.mark.asyncio
# async def test_task_status(client: TestClient, storage: StorageService):
#     service_task_copy = service_task.copy()
#
#     with open("tests/test.jpg", "rb") as file:
#         file_key = await storage.upload(
#             file,
#             ".jpg",
#             service_task_copy["s3_region"],
#             service_task_copy["s3_secret_access_key"],
#             service_task_copy["s3_access_key_id"],
#             service_task_copy["s3_host"],
#             service_task_copy["s3_bucket"],
#         )
#
#         service_task_copy["task"]["data_in"] = [file_key]
#
#         compute_response = client.post("/compute", json=service_task_copy)
#         assert compute_response.status_code == 200
#
#         task_status_response = client.get(f"/status/{service_task_copy['task']['id']}")
#
#         found_at_least_once = False
#         number_of_tries = 0
#         while task_status_response.status_code == 200 and number_of_tries < 5:
#             found_at_least_once = True
#             number_of_tries += 1
#             task_status_response = client.get(f"/status/{service_task_copy['task']['id']}")
#
#         assert found_at_least_once and number_of_tries != 5
#
#
# def test_task_status_not_found(client: TestClient):
#     task_status_response = client.get("/status/00000000-0000-0000-0000-000000000000")
#
#     assert task_status_response.status_code == 404
#
#
# @pytest.mark.asyncio
# async def test_compute_queue_full(client: TestClient, storage: StorageService):
#     service_task_copy = service_task.copy()
#
#     with open("tests/test.jpg", "rb") as file:
#         file_key = await storage.upload(
#             file,
#             ".jpg",
#             service_task_copy["s3_region"],
#             service_task_copy["s3_secret_access_key"],
#             service_task_copy["s3_access_key_id"],
#             service_task_copy["s3_host"],
#             service_task_copy["s3_bucket"],
#         )
#
#         service_task_copy["task"]["data_in"] = [file_key]
#
#         compute_response = client.post("/compute", json=service_task_copy)
#         compute_response = client.post("/compute", json=service_task_copy)
#         compute_response = client.post("/compute", json=service_task_copy)
#
#         assert compute_response.status_code == 503
