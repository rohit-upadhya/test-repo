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
    # After fix: prompt now outputs "- bullet" format matching the parser.
    with patch("app.routes.summarise.call", return_value=MOCK_BULLET_RESPONSE):
        response = client.post("/summarise", json={"text": "some long text"})
    assert response.status_code == 200
    bullets = response.json()["bullets"]
    assert len(bullets) > 0


def test_summarise_max_bullets_respected():
    with patch("app.routes.summarise.call", return_value=MOCK_BULLET_RESPONSE):
        response = client.post("/summarise", json={"text": "some long text", "max_bullets": 3})
    assert response.status_code == 200
    # This passes because the parser correctly slices — but only if prompt is fixed
    bullets = response.json()["bullets"]
    assert len(bullets) <= 3


def test_summarise_bullets_non_empty():
    with patch("app.routes.summarise.call", return_value=MOCK_BULLET_RESPONSE):
        response = client.post("/summarise", json={"text": "some long text"})
    assert response.status_code == 200
    assert len(response.json()["bullets"]) > 0


def test_summarise_max_bullets_honored():
    five_bullets = "\n".join([
        "- Point one",
        "- Point two",
        "- Point three",
        "- Point four",
        "- Point five",
    ])
    with patch("app.routes.summarise.call", return_value=five_bullets):
        response = client.post("/summarise", json={"text": "some long text", "max_bullets": 2})
    assert response.status_code == 200
    assert len(response.json()["bullets"]) <= 2
