from pydantic import BaseModel


class SummariseRequest(BaseModel):
    text: str
    max_bullets: int = 5


class SummariseResponse(BaseModel):
    bullets: list[str]
    model: str


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    category: str
    model: str


class HistoryEntry(BaseModel):
    id: int
    operation: str   # "summarise" | "classify"
    input_text: str
    result: str
    model: str


VALID_CATEGORIES = {
    "bug_report", "feature_request", "question", "complaint", "praise"
}
