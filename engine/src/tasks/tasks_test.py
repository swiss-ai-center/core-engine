import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# TODO: check service-name when creating a task

# TODO: use pytest fixture to create the test DB

# TODO: check why the not found message is not correct


def test_create_task_no_body():
    response = client.post(
        "/tasks/"
    )
    assert response.status_code == 422


def test_create_task_wrong_status():
    response = client.post(
        "/tasks/",
        json={
            "service": "test-service",
            "url": "http://test-service.local",
            "data_in": [
                "http://test-service.local/test_in_1",
            ],
            "data_out": [
                "http://test-service.local/test_out_1",
            ],
            "status": "wrong-status"
        }
    )
    assert response.status_code == 422


def test_create_tasks():
    response = client.post(
        "/tasks/",
        json={
            "service": "test-service-1",
            "url": "http://test-service.local",
            "data_in": [
                "http://test-service.local/test_in_1",
            ],
            "data_out": [
                "http://test-service.local/test_out_1",
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    response = client.post(
        "/tasks/",
        json={
            "service": "test-service-1",
            "url": "http://test-service.local",
            "data_in": [
                "http://test-service.local/test_in_1",
            ],
            "data_out": [
                "http://test-service.local/test_out_1",
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "pending"


def __test_read_all_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2
    return response.json()


def __test_read_one_task():
    tasks = __test_read_all_tasks()
    task = tasks[0]
    task_id = task["id"]
    response = client.get("/tasks/" + task_id)
    assert response.status_code == 200
    assert response.json() == task
    return task_id


def test_patch_task():
    task_id = __test_read_one_task()
    response = client.patch(
        "/tasks/" + task_id,
        json={
            "status": "running"
        }
    )
    assert response.status_code == 200
    assert response.json()["updated_at"] != "null"
    assert response.json()["status"] == "running"


def test_read_task_non_existent():
    response = client.get("/items/bad_id")
    assert response.status_code == 404
    # assert response.json() == {"detail": "Task Not Found"}


def test_delete_task_non_existent():
    response = client.delete("/items/bad_id")
    assert response.status_code == 404
    # assert response.json() == {"detail": "Task Not Found"}


def test_patch_task_non_existent():
    response = client.patch("/items/bad_id")
    assert response.status_code == 404
    # assert response.json() == {"detail": "Task Not Found"}


def test_delete_task():
    task_id = __test_read_one_task()
    response = client.delete("/tasks/" + task_id)
    assert response.status_code == 204
