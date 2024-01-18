# TODO: Adapt to new pipeline structure
# import pytest
# from fastapi.testclient import TestClient
# from main import app
# from database import get_session
# from sqlmodel import Session, SQLModel, create_engine
# from sqlmodel.pool import StaticPool
# from pytest_httpserver import HTTPServer
#
#
# @pytest.fixture(name="session")
# def session_fixture():
#     engine = create_engine(
#         "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
#     )
#
#     SQLModel.metadata.create_all(engine)
#
#     with Session(engine) as session:
#         yield session
#
#
# @pytest.fixture(name="client")
# def client_fixture(session: Session):
#     def get_session_override():
#         return session
#
#     app.dependency_overrides[get_session] = get_session_override
#
#     client = TestClient(app)
#     yield client
#     app.dependency_overrides.clear()
#
#
# @pytest.fixture(name="service_instance")
# def service_instance_fixture(httpserver: HTTPServer):
#     httpserver.expect_request("/status").respond_with_json({}, status=200)
#     httpserver.expect_request("/compute").respond_with_json({}, status=200)
#
#     yield httpserver
#
#     httpserver.clear()
#
#
# service_1 = {
#   "name": "Service 1",
#   "slug": "service-1",
#   "url": "http://test-service-1.local",
#   "summary": "string",
#   "description": "string",
#   "data_in_fields": [
#     {
#       "name": "string",
#       "type": [
#         "image/jpeg"
#       ]
#     }
#   ],
#   "data_out_fields": [
#     {
#       "name": "string",
#       "type": [
#         "image/jpeg"
#       ]
#     }
#   ]
# }
#
# service_2 = {
#   "name": "Service 2",
#   "slug": "service-2",
#   "url": "http://test-service-2.local",
#   "summary": "string",
#   "description": "string",
#   "data_in_fields": [
#     {
#       "name": "string",
#       "type": [
#         "image/jpeg"
#       ]
#     }
#   ],
#   "data_out_fields": [
#     {
#       "name": "string",
#       "type": [
#         "image/jpeg"
#       ]
#     }
#   ]
# }
#
# pipeline_1 = {
#   "name": "pipeline-1",
#   "summary": "string",
#   "description": "string",
#   "services": []
# }
#
# pipeline_2 = {
#   "name": "pipeline-2",
#   "summary": "string",
#   "description": "string",
#   "services": []
# }
#
#
# def test_create_pipeline(client: TestClient, service_instance: HTTPServer):
#     service_1_copy = service_1.copy()
#     service_2_copy = service_2.copy()
#
#     service_1_copy["url"] = service_instance.url_for("")
#     service_2_copy["url"] = service_instance.url_for("")
#
#     service_response_1 = client.post("/services", json=service_1_copy)
#     service_response_2 = client.post("/services", json=service_2_copy)
#
#     pipeline_1["services"] = []
#     pipeline_1["services"].append(service_response_1.json()["id"])
#     pipeline_1["services"].append(service_response_2.json()["id"])
#
#     pipeline_response = client.post("/pipelines", json=pipeline_1)
#
#     assert pipeline_response.status_code == 200
#
#
# def test_get_pipeline(client: TestClient, service_instance: HTTPServer):
#     service_1_copy = service_1.copy()
#     service_2_copy = service_2.copy()
#
#     service_1_copy["url"] = service_instance.url_for("")
#     service_2_copy["url"] = service_instance.url_for("")
#
#     service_response_1 = client.post("/services", json=service_1_copy)
#     service_response_2 = client.post("/services", json=service_2_copy)
#
#     pipeline_1["services"] = []
#     pipeline_1["services"].append(service_response_1.json()["id"])
#     pipeline_1["services"].append(service_response_2.json()["id"])
#
#     pipeline_response = client.post("/pipelines", json=pipeline_1)
#     pipeline_response_data = pipeline_response.json()
#     pipeline_response = client.get(f"/pipelines/{pipeline_response_data['id']}")
#
#     assert pipeline_response.status_code == 200
#
#
# def test_get_pipelines(client: TestClient, service_instance: HTTPServer):
#     service_1_copy = service_1.copy()
#     service_2_copy = service_2.copy()
#
#     service_1_copy["url"] = service_instance.url_for("")
#     service_2_copy["url"] = service_instance.url_for("")
#
#     service_response_1 = client.post("/services", json=service_1_copy)
#     service_response_2 = client.post("/services", json=service_2_copy)
#
#     pipeline_1["services"] = []
#     pipeline_1["services"].append(service_response_1.json()["id"])
#     pipeline_1["services"].append(service_response_2.json()["id"])
#     pipeline_2["services"] = []
#     pipeline_2["services"].append(service_response_1.json()["id"])
#     pipeline_2["services"].append(service_response_2.json()["id"])
#
#     client.post("/pipelines", json=pipeline_1)
#     client.post("/pipelines", json=pipeline_2)
#
#     pipelines_response = client.get("/pipelines")
#     pipelines_response_data = pipelines_response.json()
#
#     assert pipelines_response.status_code == 200
#     assert len(pipelines_response_data) == 2
#
#
# def test_delete_pipeline(client: TestClient, service_instance: HTTPServer):
#     service_1_copy = service_1.copy()
#     service_2_copy = service_2.copy()
#
#     service_1_copy["url"] = service_instance.url_for("")
#     service_2_copy["url"] = service_instance.url_for("")
#
#     service_response_1 = client.post("/services", json=service_1_copy)
#     service_response_2 = client.post("/services", json=service_2_copy)
#
#     pipeline_1["services"] = []
#     pipeline_1["services"].append(service_response_1.json()["id"])
#     pipeline_1["services"].append(service_response_2.json()["id"])
#
#     pipeline_response = client.post("/pipelines", json=pipeline_1)
#     pipeline_response_data = pipeline_response.json()
#
#     pipeline_response = client.delete(f"/pipelines/{pipeline_response_data['id']}")
#
#     assert pipeline_response.status_code == 204
#
#
# def test_update_pipeline(client: TestClient, service_instance: HTTPServer):
#     service_1_copy = service_1.copy()
#     service_2_copy = service_2.copy()
#
#     service_1_copy["url"] = service_instance.url_for("")
#     service_2_copy["url"] = service_instance.url_for("")
#
#     service_response_1 = client.post("/services", json=service_1_copy)
#     service_response_2 = client.post("/services", json=service_2_copy)
#
#     pipeline_1["services"] = []
#     pipeline_1["services"].append(service_response_1.json()["id"])
#     pipeline_1["services"].append(service_response_2.json()["id"])
#
#     pipeline_response = client.post("/pipelines", json=pipeline_1)
#     pipeline_response_data = pipeline_response.json()
#
#     pipeline_response = client.patch(
#         f"/pipelines/{pipeline_response_data['id']}",
#         json={
#             "summary": "new summary"
#         }
#     )
#     pipeline_response_data = pipeline_response.json()
#
#     assert pipeline_response.status_code == 200
#     assert pipeline_response_data["updated_at"] != "null"
#     assert pipeline_response_data["summary"] == "new summary"
#
#
# def test_create_pipeline_no_body(client: TestClient):
#     response = client.post("/pipelines")
#
#     assert response.status_code == 422
#
#
# def test_read_pipeline_non_existent(client: TestClient):
#     response = client.get("/pipelines/00000000-0000-0000-0000-000000000000")
#
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Pipeline Not Found"}
#
#
# def test_delete_pipeline_non_existent(client: TestClient):
#     response = client.delete("/pipelines/00000000-0000-0000-0000-000000000000")
#
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Pipeline Not Found"}
#
#
# def test_patch_pipeline_non_existent(client: TestClient):
#     response = client.patch("/pipelines/00000000-0000-0000-0000-000000000000", json={"status": "running"})
#
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Pipeline Not Found"}
#
#
# def test_read_pipeline_non_processable(client: TestClient):
#     response = client.get("/pipelines/bad_id")
#
#     assert response.status_code == 422
#     assert response.json()["detail"][0]["type"] == "uuid_parsing"
#
#
# def test_delete_pipeline_non_processable(client: TestClient):
#     response = client.delete("/pipelines/bad_id")
#
#     assert response.status_code == 422
#     assert response.json()["detail"][0]["type"] == "uuid_parsing"
#
#
# def test_patch_pipeline_non_processable(client: TestClient):
#     response = client.patch("/pipelines/bad_id", json={"status": "running"})
#
#     assert response.status_code == 422
#     assert response.json()["detail"][0]["type"] == "uuid_parsing"
