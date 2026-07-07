from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.routes.tone import VALID_TONES

client = TestClient(app)


def test_tone_valid_single_word():
    with patch("app.routes.tone.call", return_value="positive"):
        response = client.post("/tone", json={"text": "I love this product!"})
    assert response.status_code == 200
    assert response.json()["tone"] == "positive"


def test_tone_returns_200_for_valid_tone():
    with patch("app.routes.tone.call", return_value="positive"):
        response = client.post("/tone", json={"text": "I love this!"})
    assert response.status_code == 200
    assert response.json()["tone"] == "positive"


def test_tone_value_in_valid_tones():
    for tone in ["positive", "negative", "neutral", "mixed"]:
        with patch("app.routes.tone.call", return_value=tone):
            response = client.post("/tone", json={"text": "some text"})
        assert response.status_code == 200
        assert response.json()["tone"] in VALID_TONES
