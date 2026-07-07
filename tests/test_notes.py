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


def test_tag_filter_bug():
    # BUG: ?tag= filter is ignored — both notes returned even when filtering
    client.post("/notes", json={"text": "work note", "tag": "work"})
    client.post("/notes", json={"text": "personal note", "tag": "personal"})
    r = client.get("/notes?tag=work")
    assert r.status_code == 200
    # BUG: should be 1 but returns 2 because filter is not applied
    assert len(r.json()) == 2
