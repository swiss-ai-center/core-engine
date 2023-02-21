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

pipeline_1 = {
  "name": "pipeline-1",
  "summary": "string",
  "description": "string",
  "services": []
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


def test_stats_empty(client: TestClient):
    stats_response = client.get("/stats")
    stats_response_data = stats_response.json()

    assert stats_response.status_code == 200
    assert len(stats_response_data["services"]) == 0
    # TODO: uncomment when pipelines are implemented
    # assert len(stats_response_data["pipelines"]) == 0


def test_stats(client: TestClient, service_instance: HTTPServer):
    service_1_copy = service_1.copy()
    service_2_copy = service_2.copy()

    service_1_copy["url"] = service_instance.url_for("")
    service_2_copy["url"] = service_instance.url_for("")

    service_response_1 = client.post("/services", json=service_1_copy)
    service_response_2 = client.post("/services", json=service_2_copy)

    # TODO: uncomment when pipelines are implemented
    # pipeline_1["services"] = []
    # pipeline_1["services"].append(service_response_1.json()["id"])
    # pipeline_1["services"].append(service_response_2.json()["id"])
    #
    # pipeline_response = client.post("/pipelines", json=pipeline_1)

    task_1["service_id"] = service_response_1.json()["id"]
    task_2["service_id"] = service_response_2.json()["id"]
    # task_2["pipeline_id"] = pipeline_response.json()["id"]

    client.post("/tasks", json=task_1)
    task_response = client.post("/tasks", json=task_2)
    client.patch(
      f'/tasks/{task_response.json()["id"]}',
      json={
        "status": "finished",
        "data_out": [
          "http://test-service-1.local/test_out",
        ],
      },
    )

    stats_response = client.get("/stats")
    stats_response_data = stats_response.json()

    # assert pipeline_response.status_code == 200
    for status in stats_response_data["summary"]:
        if status["status"] == "finished":
            assert status["count"] == 1
        elif status["status"] == "pending":
            assert status["count"] == 1
    assert len(stats_response_data["services"]) == 2
    # assert len(stats_response_data["pipelines"]) == 1
    for service in stats_response_data["services"]:
        if service["service_name"] == service_1["name"]:
            assert service["total"] == 1
    # assert stats_response_data["pipelines"][pipeline_1["name"]] == 1

    client.post("/tasks", json=task_1)
    task_response = client.post("/tasks", json=task_2)
    client.patch(
      f'/tasks/{task_response.json()["id"]}',
      json={
        "status": "processing",
        "data_out": [
            "http://test-service-1.local/test_out",
        ],
      },
    )

    stats_response = client.get("/stats")
    stats_response_data = stats_response.json()

    for status in stats_response_data["summary"]:
        if status["status"] == "finished":
            assert status["count"] == 1
        elif status["status"] == "pending":
            assert status["count"] == 2
        elif status["status"] == "processing":
            assert status["count"] == 1
    assert len(stats_response_data["services"]) == 2
    # assert len(stats_response_data["pipelines"]) == 1
    for service in stats_response_data["services"]:
        if service["service_name"] == service_1["name"]:
            assert service["total"] == 2
    # assert stats_response_data["pipelines"][pipeline_1["name"]] == 2

    client.patch(
      f'/tasks/{task_response.json()["id"]}',
      json={
        "status": "error",
        "data_out": [
            "http://test-service-1.local/test_out",
        ],
      },
    )

    stats_response = client.get("/stats")
    stats_response_data = stats_response.json()

    for status in stats_response_data["summary"]:
        if status["status"] == "finished":
            assert status["count"] == 1
        elif status["status"] == "pending":
            assert status["count"] == 2
        elif status["status"] == "error":
            assert status["count"] == 1
    assert len(stats_response_data["services"]) == 2
    # assert len(stats_response_data["pipelines"]) == 1
    for service in stats_response_data["services"]:
        if service["service_name"] == service_1["name"]:
            assert service["total"] == 2
    # assert stats_response_data["pipelines"][pipeline_1["name"]] == 2

    client.patch(
      f'/tasks/{task_response.json()["id"]}',
      json={
        "status": "unavailable",
        "data_out": [
            "http://test-service-1.local/test_out",
        ],
      },
    )

    stats_response = client.get("/stats")
    stats_response_data = stats_response.json()

    for status in stats_response_data["summary"]:
        if status["status"] == "finished":
            assert status["count"] == 1
        elif status["status"] == "pending":
            assert status["count"] == 2
        elif status["status"] == "unavailable":
            assert status["count"] == 1
    assert len(stats_response_data["services"]) == 2
    # assert len(stats_response_data["pipelines"]) == 1
    for service in stats_response_data["services"]:
        if service["service_name"] == service_1["name"]:
            assert service["total"] == 2
    # assert stats_response_data["pipelines"][pipeline_1["name"]] == 2

    client.patch(
        f'/tasks/{task_response.json()["id"]}',
        json={
            "status": "saving",
            "data_out": [
                "http://test-service-1.local/test_out",
            ],
        },
    )

    stats_response = client.get("/stats")
    stats_response_data = stats_response.json()

    for status in stats_response_data["summary"]:
        if status["status"] == "finished":
            assert status["count"] == 1
        elif status["status"] == "pending":
            assert status["count"] == 2
        elif status["status"] == "saving":
            assert status["count"] == 1
    assert len(stats_response_data["services"]) == 2
    # assert len(stats_response_data["pipelines"]) == 1
    for service in stats_response_data["services"]:
        if service["service_name"] == service_1["name"]:
            assert service["total"] == 2
    # assert stats_response_data["pipelines"][pipeline_1["name"]] == 2

    client.patch(
        f'/tasks/{task_response.json()["id"]}',
        json={
            "status": "fetching",
            "data_out": [
                "http://test-service-1.local/test_out",
            ],
        },
    )

    stats_response = client.get("/stats")
    stats_response_data = stats_response.json()

    for status in stats_response_data["summary"]:
        if status["status"] == "finished":
            assert status["count"] == 1
        elif status["status"] == "pending":
            assert status["count"] == 2
        elif status["status"] == "fetching":
            assert status["count"] == 1
    assert len(stats_response_data["services"]) == 2
    # assert len(stats_response_data["pipelines"]) == 1
    for service in stats_response_data["services"]:
        if service["service_name"] == service_1["name"]:
            assert service["total"] == 2
    # assert stats_response_data["pipelines"][pipeline_1["name"]] == 2
