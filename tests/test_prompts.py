from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_prompts():
    r = client.get("/prompts")
    assert r.status_code == 200
    assert "greeting" in r.json()
    assert "farewell" in r.json()


def test_get_prompt():
    r = client.get("/prompts/greeting")
    assert r.status_code == 200
    assert "content" in r.json()


def test_get_prompt_not_found():
    assert client.get("/prompts/nonexistent").status_code == 404


def test_update_prompt():
    r = client.put("/prompts/greeting", json={"name": "greeting", "content": "Hi there!"})
    assert r.status_code == 200
    assert client.get("/prompts/greeting").json()["content"] == "Hi there!"
