from pydantic import BaseModel


class NoteIn(BaseModel):
    text: str
    tag: str = "general"


class Note(BaseModel):
    id: int
    text: str
    tag: str
    done: bool = False
    archived: bool = False


class PromptConfig(BaseModel):
    name: str
    content: str
