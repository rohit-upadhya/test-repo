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


def test_create_and_get_note():
    r = client.post("/notes", json={"text": "hello", "tag": "work"})
    assert r.status_code == 201
    assert r.json()["id"] == 1
    assert r.json()["tag"] == "work"


def test_get_note_not_found():
    assert client.get("/notes/999").status_code == 404


def test_delete_note():
    client.post("/notes", json={"text": "bye"})
    assert client.delete("/notes/1").status_code == 204
    assert client.get("/notes/1").status_code == 404


def test_list_all_notes():
    client.post("/notes", json={"text": "a", "tag": "work"})
    client.post("/notes", json={"text": "b", "tag": "personal"})
    r = client.get("/notes")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_tag_filter_returns_matching_notes():
    client.post("/notes", json={"text": "work note", "tag": "work"})
    client.post("/notes", json={"text": "personal note", "tag": "personal"})
    r = client.get("/notes?tag=work")
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 1
    assert notes[0]["tag"] == "work"


def test_tag_filter_no_param_returns_all():
    client.post("/notes", json={"text": "work note", "tag": "work"})
    client.post("/notes", json={"text": "personal note", "tag": "personal"})
    r = client.get("/notes")
    assert r.status_code == 200
    tags = {n["tag"] for n in r.json()}
    assert tags == {"work", "personal"}


def test_tag_filter_nonexistent_returns_empty():
    client.post("/notes", json={"text": "work note", "tag": "work"})
    r = client.get("/notes?tag=nonexistent")
    assert r.status_code == 200
    assert r.json() == []
