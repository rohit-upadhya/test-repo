from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_tone_valid_single_word():
    with patch("app.routes.tone.call", return_value="positive"):
        response = client.post("/tone", json={"text": "I love this product!"})
    assert response.status_code == 200
    assert response.json()["tone"] == "positive"


def test_tone_no_422_on_valid_model_output():
    for tone in ("positive", "negative", "neutral", "mixed"):
        with patch("app.routes.tone.call", return_value=tone):
            response = client.post("/tone", json={"text": "I love this!"})
        assert response.status_code == 200
        assert response.json()["tone"] == tone
