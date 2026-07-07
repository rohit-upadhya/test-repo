from fastapi import APIRouter, HTTPException
from app.models import ClassifyRequest, ClassifyResponse, VALID_CATEGORIES
from app.services.claude_client import call, load_prompt, DEFAULT_MODEL

router = APIRouter()


@router.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest) -> ClassifyResponse:
    system = load_prompt("classify.txt")
    raw = call(system, req.text).lower().strip()
    # BUG: does not validate that raw is in VALID_CATEGORIES before returning.
    # Should raise HTTPException(422) if raw not in VALID_CATEGORIES.
    return ClassifyResponse(category=raw, model=DEFAULT_MODEL)
