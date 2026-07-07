from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

# What the prompt currently produces (### header format)
MOCK_HEADER_RESPONSE = "### Point 1\nExplains the concept clearly\n\n### Point 2\nProvides useful examples\n\n### Point 3\nCovers edge cases"

# What the prompt SHOULD produce after fix (- bullet format)
MOCK_BULLET_RESPONSE = "- Explains the concept clearly\n- Provides useful examples\n- Covers edge cases\n- Easy to follow\n- Well structured overall"


def test_summarise_returns_200():
    with patch("app.routes.summarise.call", return_value=MOCK_BULLET_RESPONSE):
        response = client.post("/summarise", json={"text": "some long text"})
    assert response.status_code == 200


def test_summarise_empty_bullets_due_to_prompt_mismatch_bug():
    # BUG: prompt outputs "### Header" format but parser expects "- bullet" lines.
    # Result: bullets is always [] when the real model responds.
    with patch("app.routes.summarise.call", return_value=MOCK_HEADER_RESPONSE):
        response = client.post("/summarise", json={"text": "some long text"})
    assert response.status_code == 200
    # BUG: empty because prompt format doesn't match parser
    assert response.json()["bullets"] == []


def test_summarise_max_bullets_respected():
    with patch("app.routes.summarise.call", return_value=MOCK_BULLET_RESPONSE):
        response = client.post("/summarise", json={"text": "some long text", "max_bullets": 3})
    assert response.status_code == 200
    # This passes because the parser correctly slices — but only if prompt is fixed
    bullets = response.json()["bullets"]
    assert len(bullets) <= 3
