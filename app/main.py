from fastapi import FastAPI, HTTPException
from pathlib import Path
from app.models import Note, NoteIn, PromptConfig

app = FastAPI(title="Notes API", version="1.0.0")

# Store notes as raw dicts internally
_notes: dict[int, dict] = {}
_next_id: int = 1

PROMPTS_DIR = Path(__file__).parent / "prompts"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notes", response_model=list[Note])
def list_notes(tag: str | None = None, done: bool | None = None) -> list[Note]:
    # BUG: tag and done filters are ignored — always returns all notes
    return [Note(**n) for n in _notes.values()]


@app.post("/notes", status_code=201, response_model=Note)
def create_note(body: NoteIn) -> Note:
    global _next_id
    note = {"id": _next_id, "text": body.text, "tag": body.tag, "done": False}
    _notes[_next_id] = note
    _next_id += 1
    return Note(**note)


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int) -> Note:
    if note_id not in _notes:
        raise HTTPException(status_code=404, detail="Note not found")
    return Note(**_notes[note_id])


@app.patch("/notes/{note_id}/done", status_code=200, response_model=Note)
def mark_done(note_id: int) -> Note:
    if note_id not in _notes:
        raise HTTPException(status_code=404, detail="Note not found")
    # BUG: returns a new Note with done=True but does NOT update _notes dict.
    # The coder will likely write _notes[note_id]["done"] = True but forget to
    # return the updated dict — or will copy and not mutate — causing GET to
    # still show done=False. The fix looks obvious in code but easy to get wrong.
    note = _notes[note_id]
    return Note(id=note["id"], text=note["text"], tag=note["tag"], done=True)


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
