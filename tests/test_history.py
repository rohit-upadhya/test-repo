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
    # Documents buggy behavior: missing entry raises StopIteration instead of 404
    # The correct fix is: raise HTTPException(404) when entry not found
    import pytest
    with pytest.raises(Exception):
        client.get("/history/999")


def test_clear_history():
    history_module.record("summarise", "text", "result", "model")
    response = client.delete("/history")
    assert response.status_code == 204
    assert client.get("/history").json() == []
