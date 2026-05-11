"""Scraper orchestrator: read channels, embed messages, index into Qdrant.

Resumable: stores the last-indexed message_id per channel in scraper/.state.json
so re-runs only fetch new messages.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from client import build_client, iter_channel_messages
from embedder import embed_batch
from indexer import MessageRecord, ensure_collection, get_client, upsert_messages

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHANNELS_FILE = PROJECT_ROOT / "shared" / "channels.json"
STATE_FILE = Path(__file__).resolve().parent / ".state.json"

BATCH_SIZE = 100


def load_channels() -> list[dict]:
    with CHANNELS_FILE.open(encoding="utf-8") as f:
        return json.load(f)["channels"]


def load_state() -> dict[str, int]:
    if not STATE_FILE.exists():
        return {}
    with STATE_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict[str, int]) -> None:
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _build_records(channel: str, messages: list, vectors: list[list[float]]) -> list[MessageRecord]:
    records: list[MessageRecord] = []
    for m, v in zip(messages, vectors):
        records.append({
            "channel": channel,
            "message_id": m.id,
            "text": m.message,
            "vector": v,
            "date": m.date.isoformat() if m.date else None,
            "url": f"https://t.me/{channel}/{m.id}",
            "sender_id": getattr(m, "sender_id", None),
            "reply_to": m.reply_to.reply_to_msg_id if m.reply_to else None,
        })
    return records


async def process_channel(tg, qdrant, channel: str, state: dict[str, int]) -> None:
    last_seen = state.get(channel, 0)
    buffer = []          # messages with non-empty text, waiting to be embedded
    highest_id = last_seen  # advances even past skipped messages

    print(f"[{channel}] resuming from message_id > {last_seen}")

    async def flush():
        nonlocal buffer
        if not buffer:
            return
        vectors = embed_batch([m.message for m in buffer])
        n = upsert_messages(qdrant, _build_records(channel, buffer, vectors))
        state[channel] = highest_id
        save_state(state)
        print(f"[{channel}] indexed batch of {n}, cursor={highest_id}")
        buffer = []

    async for msg in iter_channel_messages(tg, channel, min_id=last_seen):
        highest_id = max(highest_id, msg.id)
        text = (msg.message or "").strip()
        if not text:
            continue
        buffer.append(msg)
        if len(buffer) >= BATCH_SIZE:
            await flush()

    await flush()
    # Even if no batches were flushed, persist cursor in case we skipped media-only msgs.
    state[channel] = highest_id
    save_state(state)
    print(f"[{channel}] done, final cursor={highest_id}")


async def main() -> None:
    channels = [c for c in load_channels() if c.get("enabled", True)]
    if not channels:
        print("No enabled channels in shared/channels.json — nothing to do.")
        return

    state = load_state()
    qdrant = get_client()
    ensure_collection(qdrant)
    tg = build_client()

    async with tg:
        for ch in channels:
            try:
                await process_channel(tg, qdrant, ch["username"], state)
            except Exception as e:
                print(f"[{ch['username']}] FAILED: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
