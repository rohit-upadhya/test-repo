from pydantic import BaseModel


class NoteIn(BaseModel):
    text: str
    tag: str = "general"
    priority: int = 2


class Note(BaseModel):
    id: int
    text: str
    tag: str
    done: bool = False
    archived: bool = False
    priority: int = 2


class PromptConfig(BaseModel):
    name: str
    content: str
