"""Gemini embeddings wrapper for the NTI scraper.

Uses gemini-embedding-001 with output_dimensionality=768 (MRL-truncated)
so the Qdrant collection (768-dim, cosine) stays valid.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv
from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = "gemini-embedding-001"
VECTOR_SIZE = 768

_api_key = (os.getenv("Gemini_api_key") or "").strip()
_client: genai.Client | None = genai.Client(api_key=_api_key) if _api_key else None


def _config(task_type: str) -> types.EmbedContentConfig:
    return types.EmbedContentConfig(
        task_type=task_type,
        output_dimensionality=VECTOR_SIZE,
    )


def embed_text(text: str, *, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """Embed a single string. Use task_type='RETRIEVAL_QUERY' for search queries."""
    if _client is None:
        raise RuntimeError("Gemini_api_key is not set in .env")
    result = _client.models.embed_content(
        model=MODEL, contents=text, config=_config(task_type)
    )
    return list(result.embeddings[0].values)


def embed_batch(
    texts: Sequence[str], *, task_type: str = "RETRIEVAL_DOCUMENT"
) -> list[list[float]]:
    """Embed multiple strings in one API call."""
    if _client is None:
        raise RuntimeError("Gemini_api_key is not set in .env")
    result = _client.models.embed_content(
        model=MODEL, contents=list(texts), config=_config(task_type)
    )
    return [list(e.values) for e in result.embeddings]


def _smoke_test() -> None:
    if _client is None:
        raise SystemExit(
            "Gemini_api_key is empty in .env — get one at https://aistudio.google.com/app/apikey"
        )
    vec = embed_text("Hello, world.")
    assert len(vec) == VECTOR_SIZE, f"expected {VECTOR_SIZE} dims, got {len(vec)}"
    print(f"Embedding OK: {len(vec)} dims, first 5: {vec[:5]}")


if __name__ == "__main__":
    _smoke_test()
