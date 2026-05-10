"""Gemini text-embedding-004 wrapper for the NTI scraper."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

import google.generativeai as genai
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = "models/text-embedding-004"
VECTOR_SIZE = 768

_api_key = (os.getenv("Gemini_api_key") or "").strip()
if _api_key:
    genai.configure(api_key=_api_key)


def embed_text(text: str, *, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """Embed a single string. Use task_type='RETRIEVAL_QUERY' for search queries."""
    result = genai.embed_content(model=MODEL, content=text, task_type=task_type)
    return result["embedding"]


def embed_batch(texts: Sequence[str], *, task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Embed multiple strings in one API call."""
    result = genai.embed_content(model=MODEL, content=list(texts), task_type=task_type)
    return result["embedding"]


def _smoke_test() -> None:
    if not _api_key:
        raise SystemExit(
            "Gemini_api_key is empty in .env — get one at https://aistudio.google.com/app/apikey"
        )
    vec = embed_text("Hello, world.")
    assert len(vec) == VECTOR_SIZE, f"expected {VECTOR_SIZE} dims, got {len(vec)}"
    print(f"Embedding OK: {len(vec)} dims, first 5: {vec[:5]}")


if __name__ == "__main__":
    _smoke_test()
