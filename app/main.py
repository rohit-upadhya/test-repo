from fastapi import FastAPI, HTTPException
from pathlib import Path
from app.models import Note, NoteIn, PromptConfig

app = FastAPI(title="Notes API", version="1.0.0")

_notes: dict[int, Note] = {}
_next_id: int = 1

PROMPTS_DIR = Path(__file__).parent / "prompts"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notes", response_model=list[Note])
def list_notes(tag: str | None = None) -> list[Note]:
    # BUG: tag filter is ignored — always returns all notes
    return list(_notes.values())


@app.post("/notes", status_code=201, response_model=Note)
def create_note(body: NoteIn) -> Note:
    global _next_id
    note = Note(id=_next_id, text=body.text, tag=body.tag)
    _notes[_next_id] = note
    _next_id += 1
    return note


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int) -> Note:
    if note_id not in _notes:
        raise HTTPException(status_code=404, detail="Note not found")
    return _notes[note_id]


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    if note_id not in _notes:
        raise HTTPException(status_code=404, detail="Note not found")
    del _notes[note_id]


# Prompt management endpoints
@app.get("/prompts", response_model=list[str])
def list_prompts() -> list[str]:
    return [f.stem for f in PROMPTS_DIR.glob("*.txt")]


@app.get("/prompts/{name}")
def get_prompt(name: str) -> dict:
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' not found")
    return {"name": name, "content": path.read_text()}


@app.put("/prompts/{name}")
def update_prompt(name: str, body: PromptConfig) -> dict:
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' not found")
    path.write_text(body.content)
    return {"name": name, "updated": True}
