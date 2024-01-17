import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_session
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from pytest_httpserver import HTTPServer


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="service_instance")
def service_instance_fixture(httpserver: HTTPServer):
    httpserver.expect_request("/status").respond_with_json({}, status=200)
    httpserver.expect_request("/compute").respond_with_json({}, status=200)

    yield httpserver

    httpserver.clear()


service_1 = {
    "name": "Service 1",
    "slug": "service-1",
    "url": "http://test-service-1.local",
    "summary": "string",
    "description": "string",
    "data_in_fields": [
        {
            "name": "string",
            "type": [
                "image/jpeg"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "string",
            "type": [
                "image/jpeg"
            ]
        }
    ]
}

task_1 = {
    "service_id": None,
    "data_in": [
        "http://test-service-1.local/test_in",
    ],
    "data_out": [
        "http://test-service-1.local/test_out",
    ]
}

task_2 = {
    "service_id": None,
    "data_in": [
        "http://test-service-2.local/test_in",
    ],
    "data_out": [
        "http://test-service-2.local/test_out",
    ]
}


def test_create_task(client: TestClient, service_instance: HTTPServer):
    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    service_response = client.post("/services", json=service_copy)
    service_response_data = service_response.json()

    task_1["service_id"] = service_response_data["id"]

    task_response = client.post("/tasks", json=task_1)
    task_response_data = task_response.json()

    assert task_response.status_code == 200
    assert task_response_data["status"] == "pending"
    assert task_response_data["service_id"] == service_response_data["id"]
    assert task_response_data["service"]["name"] == service_response_data["name"]


def test_get_task(client: TestClient, service_instance: HTTPServer):
    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    service_response = client.post("/services", json=service_copy)
    service_response_data = service_response.json()

    task_1["service_id"] = service_response_data["id"]

    task_response = client.post("/tasks", json=task_1)
    task_response_data = task_response.json()

    task_response = client.get(f"/tasks/{task_response_data['id']}")
    task_response_data = task_response.json()

    assert task_response.status_code == 200
    assert task_response_data["status"] == "pending"


def test_get_tasks(client: TestClient, service_instance: HTTPServer):
    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    service_response = client.post("/services", json=service_copy)
    service_response_data = service_response.json()

    task_1["service_id"] = service_response_data["id"]
    task_2["service_id"] = service_response_data["id"]

    client.post("/tasks/", json=task_1)
    client.post("/tasks/", json=task_2)

    tasks_response = client.get("/tasks")
    tasks_response_data = tasks_response.json()

    assert tasks_response.status_code == 200
    assert len(tasks_response_data) == 2


def test_delete_task(client: TestClient, service_instance: HTTPServer):
    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    service_response = client.post("/services", json=service_copy)
    service_response_data = service_response.json()

    task_1["service_id"] = service_response_data["id"]

    task_response = client.post("/tasks", json=task_1)
    task_response_data = task_response.json()

    task_response = client.delete(f"/tasks/{task_response_data['id']}")

    assert task_response.status_code == 204


def test_update_task(client: TestClient, service_instance: HTTPServer):
    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    service_response = client.post("/services", json=service_copy)
    service_response_data = service_response.json()

    task_1["service_id"] = service_response_data["id"]

    task_response = client.post("/tasks", json=task_1)
    task_response_data = task_response.json()

    task_response = client.patch(
        f"/tasks/{task_response_data['id']}",
        json={
            "status": "processing",
            "data_out": [
                "http://test-service-1.local/test_out",
            ]
        }
    )
    task_response_data = task_response.json()

    assert task_response.status_code == 200
    assert task_response_data["updated_at"] != "null"
    assert task_response_data["status"] == "processing"


def test_create_task_no_body(client: TestClient):
    response = client.post("/tasks")

    assert response.status_code == 422


def test_create_task_wrong_status(client: TestClient):
    task_1["status"] = "wrong-status"
    response = client.post("/tasks", json=task_1)

    assert response.status_code == 422


def test_read_task_non_existent(client: TestClient):
    response = client.get("/tasks/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task Not Found"}


def test_delete_task_non_existent(client: TestClient):
    response = client.delete("/tasks/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task Not Found"}


def test_patch_task_non_existent(client: TestClient):
    response = client.patch(
        "/tasks/00000000-0000-0000-0000-000000000000",
        json={
            "status": "processing",
            "data_out": [
                "http://test-service-1.local/test_out",
            ],
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task Not Found"}


def test_read_task_non_processable(client: TestClient):
    response = client.get("/tasks/bad_id")

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "uuid_parsing"


def test_delete_task_non_processable(client: TestClient):
    response = client.delete("/tasks/bad_id")

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "uuid_parsing"


def test_patch_task_non_processable(client: TestClient):
    response = client.patch(
        "/tasks/bad_id",
        json={
            "status": "running",
            "data_out": [
                "http://test-service-1.local/test_out",
            ],
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "uuid_parsing"
