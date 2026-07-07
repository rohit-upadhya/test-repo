from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_tone_valid_single_word():
    with patch("app.routes.tone.call", return_value="positive"):
        response = client.post("/tone", json={"text": "I love this product!"})
    assert response.status_code == 200
    assert response.json()["tone"] == "positive"


def test_tone_prompt_returns_sentence_bug():
    # BUG: prompt is not strict enough — model returns a sentence like
    # "The tone is positive." instead of just "positive".
    # The validation rejects it with 422.
    # Fix: tighten prompts/tone.txt to enforce single-word output.
    with patch("app.routes.tone.call", return_value="the tone is positive."):
        response = client.post("/tone", json={"text": "I love this!"})
    # BUG: returns 422 when it should return 200 after prompt is fixed
    assert response.status_code == 422
