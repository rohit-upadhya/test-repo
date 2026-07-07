from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_classify_valid_category():
    with patch("app.routes.classify.call", return_value="bug_report"):
        response = client.post("/classify", json={"text": "the app crashes on startup"})
    assert response.status_code == 200
    assert response.json()["category"] == "bug_report"


def test_classify_invalid_category_not_validated_bug():
    # Documents buggy behavior: invalid category is returned without validation
    with patch("app.routes.classify.call", return_value="gibberish"):
        response = client.post("/classify", json={"text": "some text"})
    # BUG: should return 422, but returns 200 with invalid category
    assert response.status_code == 200
    assert response.json()["category"] == "gibberish"
