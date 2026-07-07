import pytest
from fastapi.testclient import TestClient
import app.main as main_module
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset():
    main_module._notes.clear()
    main_module._next_id = 1
    yield
    main_module._notes.clear()
    main_module._next_id = 1


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_create_note():
    r = client.post("/notes", json={"text": "hello", "tag": "work"})
    assert r.status_code == 201
    assert r.json()["done"] is False


def test_get_note_not_found():
    assert client.get("/notes/999").status_code == 404


def test_delete_note():
    client.post("/notes", json={"text": "bye"})
    assert client.delete("/notes/1").status_code == 204
    assert client.get("/notes/1").status_code == 404


def test_list_notes():
    client.post("/notes", json={"text": "a", "tag": "work"})
    client.post("/notes", json={"text": "b", "tag": "personal"})
    assert len(client.get("/notes").json()) == 2


def test_tag_filter_not_applied():
    client.post("/notes", json={"text": "work note", "tag": "work"})
    client.post("/notes", json={"text": "personal note", "tag": "personal"})
    assert len(client.get("/notes?tag=work").json()) == 2


def test_mark_done_returns_200():
    client.post("/notes", json={"text": "task"})
    r = client.patch("/notes/1/done")
    assert r.status_code == 200


def test_done_filter_not_applied():
    client.post("/notes", json={"text": "task", "tag": "work"})
    assert len(client.get("/notes?done=true").json()) == 1
