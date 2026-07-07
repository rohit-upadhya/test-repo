from fastapi import APIRouter, HTTPException
from app.models import HistoryEntry

router = APIRouter()

_history: list[HistoryEntry] = []
_next_id = 1


def record(operation: str, input_text: str, result: str, model: str) -> HistoryEntry:
    global _next_id
    entry = HistoryEntry(
        id=_next_id,
        operation=operation,
        input_text=input_text,
        result=result,
        model=model,
    )
    _history.append(entry)
    _next_id += 1
    return entry


@router.get("/history", response_model=list[HistoryEntry])
def get_history() -> list[HistoryEntry]:
    return _history


@router.get("/history/{entry_id}", response_model=HistoryEntry)
def get_history_entry(entry_id: int) -> HistoryEntry:
    # BUG: linear scan returns first match but does not handle
    # the case where entry_id doesn't exist — raises StopIteration
    # instead of a proper 404.
    return next(e for e in _history if e.id == entry_id)


@router.delete("/history", status_code=204)
def clear_history() -> None:
    global _next_id
    _history.clear()
    _next_id = 1
