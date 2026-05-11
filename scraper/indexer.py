"""Qdrant wrapper for the NTI scraper.

Reads collection config from shared/qdrant.json so vector size, distance,
and collection name stay in one place.
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any, Iterable, Optional, TypedDict

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

with (PROJECT_ROOT / "shared" / "qdrant.json").open(encoding="utf-8") as f:
    _CFG = json.load(f)

COLLECTION = _CFG["collection"]
VECTOR_SIZE = _CFG["vector_size"]
DISTANCE = qm.Distance[_CFG["distance"].upper()]


class MessageRecord(TypedDict, total=False):
    channel: str
    message_id: int
    text: str
    vector: list[float]
    date: str
    url: str
    sender_id: Optional[int]
    reply_to: Optional[int]


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value or not value.strip():
        raise RuntimeError(f"Missing required env var: {name}")
    return value.strip()


def get_client() -> QdrantClient:
    """Connect to Qdrant Cloud using credentials from .env."""
    return QdrantClient(url=_require("Qdrant_url"), api_key=_require("Qdrant_api_key"))


def ensure_collection(client: QdrantClient) -> None:
    """Create the collection if it doesn't exist. Idempotent."""
    if client.collection_exists(COLLECTION):
        return
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=qm.VectorParams(size=VECTOR_SIZE, distance=DISTANCE),
    )


def _point_id(channel: str, message_id: int) -> str:
    """Deterministic UUID per (channel, message_id) so re-indexing is idempotent."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{channel}/{message_id}"))


def upsert_messages(client: QdrantClient, items: Iterable[MessageRecord]) -> int:
    """Upsert a batch of embedded messages. Returns the number of points written."""
    points = []
    for it in items:
        payload: dict[str, Any] = {k: v for k, v in it.items() if k != "vector"}
        points.append(
            qm.PointStruct(
                id=_point_id(it["channel"], it["message_id"]),
                vector=it["vector"],
                payload=payload,
            )
        )
    if not points:
        return 0
    client.upsert(collection_name=COLLECTION, points=points)
    return len(points)


def search(
    client: QdrantClient,
    query_vector: list[float],
    *,
    limit: int = 10,
    channel: Optional[str] = None,
) -> list[qm.ScoredPoint]:
    """Vector search with an optional channel filter."""
    query_filter = None
    if channel:
        query_filter = qm.Filter(
            must=[qm.FieldCondition(key="channel", match=qm.MatchValue(value=channel))]
        )
    result = client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=limit,
        query_filter=query_filter,
        with_payload=True,
    )
    return result.points


def _smoke_test() -> None:
    client = get_client()
    ensure_collection(client)
    info = client.get_collection(COLLECTION)
    print(f"Collection '{COLLECTION}' OK")
    print(f"  status: {info.status}")
    print(f"  vectors: size={info.config.params.vectors.size}, distance={info.config.params.vectors.distance}")
    print(f"  points: {info.points_count}")


if __name__ == "__main__":
    _smoke_test()
