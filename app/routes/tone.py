from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.claude_client import call, load_prompt, DEFAULT_MODEL

router = APIRouter()

VALID_TONES = {"positive", "negative", "neutral", "mixed"}


class ToneRequest(BaseModel):
    text: str


class ToneResponse(BaseModel):
    tone: str
    model: str


@router.post("/tone", response_model=ToneResponse)
def analyse_tone(req: ToneRequest) -> ToneResponse:
    system = load_prompt("tone.txt")
    raw = call(system, req.text).lower().strip()
    # BUG: prompt says "Output ONLY one of: positive, negative, neutral, mixed"
    # but the model sometimes returns "The tone is positive." or similar.
    # This validation then rejects a correct answer.
    # Fix: update prompts/tone.txt to be more strict about single-word output.
    if raw not in VALID_TONES:
        raise HTTPException(
            status_code=422,
            detail=f"Model returned unexpected tone: {raw!r}. Expected one of {sorted(VALID_TONES)}"
        )
    return ToneResponse(tone=raw, model=DEFAULT_MODEL)
