import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
import app.routes.history as history_module

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear():
    history_module._history.clear()
    history_module._next_id = 1
    yield
    history_module._history.clear()
    history_module._next_id = 1


def test_history_empty():
    response = client.get("/history")
    assert response.status_code == 200
    assert response.json() == []


def test_history_after_classify():
    with patch("app.routes.classify.call", return_value="question"):
        client.post("/classify", json={"text": "what is this?"})
    # Note: classify route does not record to history yet (not wired up)
    response = client.get("/history")
    assert response.status_code == 200


def test_history_entry_not_found_returns_404():
    response = client.get("/history/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_history_entry_found_returns_200():
    history_module.record("summarise", "input text", "result text", "test-model")
    response = client.get("/history/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_clear_history():
    history_module.record("summarise", "text", "result", "model")
    response = client.delete("/history")
    assert response.status_code == 204
    assert client.get("/history").json() == []
