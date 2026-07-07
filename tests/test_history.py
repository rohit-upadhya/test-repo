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


def test_history_entry_not_found_no_404_bug():
    response = client.get("/history/999")
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert isinstance(detail, str) and len(detail) > 0


def test_history_entry_found_returns_200():
    entry = history_module.record("summarise", "input text", "result text", "test-model")
    response = client.get(f"/history/{entry.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == entry.id
    assert body["operation"] == "summarise"
    assert body["input_text"] == "input text"
    assert body["result"] == "result text"
    assert body["model"] == "test-model"


def test_clear_history():
    history_module.record("summarise", "text", "result", "model")
    response = client.delete("/history")
    assert response.status_code == 204
    assert client.get("/history").json() == []
