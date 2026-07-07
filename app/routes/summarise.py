from fastapi import APIRouter
from app.models import SummariseRequest, SummariseResponse
from app.services.claude_client import call, load_prompt, DEFAULT_MODEL

router = APIRouter()


@router.post("/summarise", response_model=SummariseResponse)
def summarise(req: SummariseRequest) -> SummariseResponse:
    system = load_prompt("summarise.txt")
    raw = call(system, req.text)
    # BUG: prompt outputs "### Header\ntext" format but this parser looks for
    # lines starting with "- ". Result: bullets is always empty list [].
    # Fix requires BOTH:
    #   1. Update prompts/summarise.txt to output "- bullet" lines
    #   2. Keep this parser OR update it to match the new prompt format
    bullets = [
        line.lstrip("-•* ").strip()
        for line in raw.splitlines()
        if line.strip().startswith("- ")
    ]
    bullets = bullets[:req.max_bullets]
    return SummariseResponse(bullets=bullets, model=DEFAULT_MODEL)
