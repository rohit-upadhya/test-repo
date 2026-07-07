from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

MOCK_RESPONSE = "- Explains the concept clearly\n- Provides useful examples\n- Covers edge cases\n- Easy to follow\n- Well structured overall"


def test_summarise_returns_bullets():
    with patch("app.routes.summarise.call", return_value=MOCK_RESPONSE):
        response = client.post("/summarise", json={"text": "some long text"})
    assert response.status_code == 200
    data = response.json()
    assert "bullets" in data
    assert len(data["bullets"]) > 0
    assert "model" in data


def test_summarise_max_bullets_ignored_bug():
    # Documents buggy behavior: max_bullets=2 is ignored, returns all 5 bullets
    with patch("app.routes.summarise.call", return_value=MOCK_RESPONSE):
        response = client.post("/summarise", json={"text": "some long text", "max_bullets": 2})
    assert response.status_code == 200
    bullets = response.json()["bullets"]
    # BUG: should be 2, but returns all 5 because max_bullets is ignored
    assert len(bullets) == 5
