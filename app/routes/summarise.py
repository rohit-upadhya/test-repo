from fastapi import APIRouter
from app.models import SummariseRequest, SummariseResponse
from app.services.claude_client import call, load_prompt, DEFAULT_MODEL

router = APIRouter()


@router.post("/summarise", response_model=SummariseResponse)
def summarise(req: SummariseRequest) -> SummariseResponse:
    system = load_prompt("summarise.txt")
    # BUG: ignores req.max_bullets — always returns whatever the model produces,
    # never truncates to max_bullets. Should slice bullets[:req.max_bullets].
    raw = call(system, req.text)
    bullets = [
        line.lstrip("-•* ").strip()
        for line in raw.splitlines()
        if line.strip()
    ]
    return SummariseResponse(bullets=bullets, model=DEFAULT_MODEL)
