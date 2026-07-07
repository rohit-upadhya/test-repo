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


def test_list_notes():
    client.post("/notes", json={"text": "a", "tag": "work"})
    client.post("/notes", json={"text": "b", "tag": "personal"})
    assert len(client.get("/notes").json()) == 2


def test_tag_filter():
    client.post("/notes", json={"text": "work note", "tag": "work"})
    client.post("/notes", json={"text": "personal note", "tag": "personal"})
    r = client.get("/notes?tag=work")
    assert len(r.json()) == 1
    assert r.json()[0]["tag"] == "work"


def test_mark_done():
    client.post("/notes", json={"text": "task"})
    r = client.patch("/notes/1/done")
    assert r.status_code == 200
    assert r.json()["done"] is True
    assert client.get("/notes/1").json()["done"] is True


def test_done_filter():
    client.post("/notes", json={"text": "task1"})
    client.post("/notes", json={"text": "task2"})
    client.patch("/notes/1/done")
    r = client.get("/notes?done=true")
    assert len(r.json()) == 1


def test_archive_note_returns_200():
    # Tests current behavior: DELETE returns 200
    client.post("/notes", json={"text": "bye"})
    r = client.delete("/notes/1")
    assert r.status_code == 200


def test_archived_note_not_in_list():
    # After DELETE the note disappears from GET /notes (both hard and soft delete pass this)
    client.post("/notes", json={"text": "bye"})
    client.delete("/notes/1")
    assert len(client.get("/notes").json()) == 0


def test_delete_returns_archived_true():
    client.post("/notes", json={"text": "archive me", "tag": "work"})
    r = client.delete("/notes/1")
    assert r.status_code == 200
    assert r.json()["archived"] is True


def test_get_after_delete_returns_archived():
    client.post("/notes", json={"text": "archive me", "tag": "work"})
    client.delete("/notes/1")
    r = client.get("/notes/1")
    assert r.status_code == 200
    assert r.json()["archived"] is True


def test_list_excludes_archived():
    client.post("/notes", json={"text": "first", "tag": "work"})
    client.post("/notes", json={"text": "second", "tag": "work"})
    client.delete("/notes/1")
    notes = client.get("/notes").json()
    assert len(notes) == 1
    assert notes[0]["id"] != 1


def test_get_note_never_created_returns_404():
    r = client.get("/notes/999")
    assert r.status_code == 404
