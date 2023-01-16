import pytest
import requests
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
@pytest.mark.anyio
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="service_instance")
def service_instance_fixture():
    http_server = HTTPServer()
    http_server.expect_request("/services/service-1/status").respond_with_json({"status": "Service is available"})


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

service_2 = {
    "name": "Service 2",
    "slug": "service-2",
    "url": "http://test-service-2.local",
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


def test_create_service(client: TestClient):
    service_response = client.post("/services", json=service_1)

    assert service_response.status_code == 200


def test_get_service(client: TestClient):
    service_response = client.post("/services", json=service_1)
    service_response_data = service_response.json()

    service_response = client.get(f"/services/{service_response_data['id']}")

    assert service_response.status_code == 200


def test_get_services(client: TestClient):
    client.post("/services/", json=service_1)
    client.post("/services/", json=service_2)

    services_response = client.get("/services")
    services_response_data = services_response.json()

    assert services_response.status_code == 200
    assert len(services_response_data) == 2


def test_delete_service(client: TestClient):
    service_response = client.post("/services", json=service_1)
    service_response_data = service_response.json()

    service_response = client.delete(f"/services/{service_response_data['id']}")

    assert service_response.status_code == 204


def test_update_service(client: TestClient):
    service_response = client.post("/services", json=service_1)
    service_response_data = service_response.json()

    service_response = client.patch(
        f"/services/{service_response_data['id']}",
        json={
            "summary": "new summary"
        }
    )
    service_response_data = service_response.json()

    assert service_response.status_code == 200
    assert service_response_data["updated_at"] != "null"
    assert service_response_data["summary"] == "new summary"


def test_create_service_no_body(client: TestClient):
    response = client.post("/services")

    assert response.status_code == 422


def test_create_service_bad_slug(client: TestClient):
    service_copy = service_1.copy()
    service_copy["slug"] = "Bad Slug"

    service_response = client.post("/services", json=service_copy)

    assert service_response.status_code == 422


def test_create_service_same_slug(client: TestClient):
    client.post("/services", json=service_1)
    service_response = client.post("/services", json=service_1)

    assert service_response.status_code == 409


def test_read_service_non_existent(client: TestClient):
    response = client.get("/services/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Service Not Found"}


def test_delete_service_non_existent(client: TestClient):
    response = client.delete("/services/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Service Not Found"}


def test_patch_service_non_existent(client: TestClient):
    response = client.patch("/services/00000000-0000-0000-0000-000000000000", json={"status": "running"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Service Not Found"}


def test_read_service_non_processable(client: TestClient):
    response = client.get("/services/bad_id")

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "type_error.uuid"


def test_delete_service_non_processable(client: TestClient):
    response = client.delete("/services/bad_id")

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "type_error.uuid"


def test_patch_service_non_processable(client: TestClient):
    response = client.patch("/services/bad_id", json={"status": "running"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "type_error.uuid"


def test_service_status(client: TestClient, service_instance: HTTPServer):
    service_response = client.post("/services", json=service_1)
    service_response_data = service_response.json()

    service_status_response = requests.get(f"/services/{service_response_data['slug']}/status")
    service_status_response_data = service_status_response.json()

    assert service_status_response.status_code == 200
    assert service_status_response_data["status"] == "Service is available"
