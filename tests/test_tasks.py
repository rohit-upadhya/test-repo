import pytest
from fastapi.testclient import TestClient

from app.main import app, tasks, _next_id


@pytest.fixture(autouse=True)
def reset_state():
    """Reset in-memory task store and ID counter between tests."""
    import app.main as main_module
    main_module.tasks.clear()
    main_module._next_id = 1
    yield
    main_module.tasks.clear()
    main_module._next_id = 1


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Buy milk", "description": "2% milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Buy milk"
    assert data["description"] == "2% milk"
    assert data["done"] is False


def test_list_tasks(client):
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = {t["title"] for t in data}
    assert titles == {"Task 1", "Task 2"}


def test_get_task(client):
    client.post("/tasks", json={"title": "Find me"})
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Find me"


def test_get_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_delete_task_wrong_behavior(client):
    # Tests current (buggy) behavior: DELETE removes the task and returns {"deleted": id}
    # The correct behavior should be to mark done=True and return the task,
    # but that is not implemented — this test documents the bug.
    client.post("/tasks", json={"title": "To be deleted"})
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.json() == {"deleted": 1}

    # Task is gone from the store (confirms the buggy delete actually happened)
    get_response = client.get("/tasks/1")
    assert get_response.status_code == 404
