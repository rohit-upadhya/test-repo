"""Thin wrapper around the Anthropic SDK for single-shot LLM calls."""

import os
from pathlib import Path

import anthropic

_client: anthropic.Anthropic | None = None

DEFAULT_MODEL = "claude-sonnet-4-6"


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def load_prompt(name: str) -> str:
    path = Path(__file__).parent.parent / "prompts" / name
    return path.read_text(encoding="utf-8")


def call(system_prompt: str, user_text: str, model: str = DEFAULT_MODEL) -> str:
    """Single-shot call. Returns the text of the first content block."""
    response = get_client().messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_text}],
    )
    return response.content[0].text.strip()
