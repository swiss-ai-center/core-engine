import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_session
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool


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


# TODO: check service-name when creating a task

task_1 = {
    "service": "test-service-1",
    "url": "http://test-service-1.local",
    "data_in": [
        "http://test-service-1.local/test_in",
    ],
    "data_out": [
        "http://test-service-1.local/test_out",
    ]
}

task_2 = {
    "service": "test-service-2",
    "url": "http://test-service-2.local",
    "data_in": [
        "http://test-service-2.local/test_in",
    ],
    "data_out": [
        "http://test-service-2.local/test_out",
    ]
}


def test_create_task(client: TestClient):
    response = client.post("/tasks", json=task_1)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "pending"


def test_get_task(client: TestClient):
    response = client.post("/tasks", json=task_1)
    response_data = response.json()

    response = client.get(f"/tasks/{response_data['id']}")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "pending"


def test_get_tasks(client: TestClient):
    client.post("/tasks/", json=task_1)
    client.post("/tasks/", json=task_2)

    response = client.get("/tasks")
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data) == 2


def test_delete_task(client: TestClient):
    response = client.post("/tasks", json=task_1)
    response_data = response.json()

    response = client.delete(f"/tasks/{response_data['id']}")

    assert response.status_code == 204


def test_update_task(client: TestClient):
    response = client.post("/tasks", json=task_1)
    response_data = response.json()

    response = client.patch(
        f"/tasks/{response_data['id']}",
        json={
            "status": "running"
        }
    )

    assert response.status_code == 200
    assert response.json()["updated_at"] != "null"
    assert response.json()["status"] == "running"


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
    response = client.patch("/tasks/00000000-0000-0000-0000-000000000000", json={"status": "running"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Task Not Found"}


def test_read_task_non_processable(client: TestClient):
    response = client.get("/tasks/bad_id")

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "type_error.uuid"


def test_delete_task_non_processable(client: TestClient):
    response = client.delete("/tasks/bad_id")

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "type_error.uuid"


def test_patch_task_non_processable(client: TestClient):
    response = client.patch("/tasks/bad_id", json={"status": "running"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "type_error.uuid"
