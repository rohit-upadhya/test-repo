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


def test_create_note_with_priority():
    r = client.post("/notes", json={"text": "important", "priority": 3})
    assert r.status_code == 201
    assert r.json()["priority"] == 3


def test_create_note_default_priority():
    r = client.post("/notes", json={"text": "normal"})
    assert r.status_code == 201
    assert r.json()["priority"] == 2


def test_sort_by_priority():
    client.post("/notes", json={"text": "low", "priority": 1})
    client.post("/notes", json={"text": "high", "priority": 3})
    r = client.get("/notes?sort=priority")
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 2
    assert notes[0]["priority"] == 3
    assert notes[1]["priority"] == 1


def test_search_returns_matching_notes():
    client.post("/notes", json={"text": "hello world"})
    client.post("/notes", json={"text": "goodbye"})
    r = client.get("/notes/search?q=hello")
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert "hello" in results[0]["text"].lower()


def test_search_case_insensitive():
    client.post("/notes", json={"text": "Hello"})
    r = client.get("/notes/search?q=hello")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_search_excludes_archived():
    client.post("/notes", json={"text": "hello"})
    # Directly set archived=True since DELETE hard-deletes (existing bug, out of scope)
    main_module._notes[1]["archived"] = True
    r = client.get("/notes/search?q=hello")
    assert r.status_code == 200
    assert len(r.json()) == 0


def test_search_no_q_returns_all_non_archived():
    client.post("/notes", json={"text": "first"})
    client.post("/notes", json={"text": "second"})
    main_module._notes[1]["archived"] = True
    r = client.get("/notes/search")
    assert r.status_code == 200
    assert len(r.json()) == 1
