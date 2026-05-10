"""Telethon client wrapper for the NTI scraper."""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.custom.message import Message

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SESSION_DIR = PROJECT_ROOT / "scraper" / ".sessions"
SESSION_DIR.mkdir(exist_ok=True)


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value or not value.strip():
        raise RuntimeError(f"Missing required env var: {name}")
    return value.strip()


def build_client(session_name: str = "nti_scraper") -> TelegramClient:
    """Construct (but don't connect) a Telethon client using credentials from .env."""
    api_id = int(_require("App_api_id"))
    api_hash = _require("App_api_hash")
    session_path = str(SESSION_DIR / session_name)
    return TelegramClient(session_path, api_id, api_hash)


async def iter_channel_messages(
    client: TelegramClient,
    channel: str,
    since: Optional[datetime] = None,
) -> AsyncIterator[Message]:
    """Yield messages from `channel` in chronological order, optionally only those after `since`."""
    async for msg in client.iter_messages(channel, reverse=True, offset_date=since):
        yield msg


async def _smoke_test() -> None:
    client = build_client()
    async with client:
        me = await client.get_me()
        print(f"Logged in as: {me.username or me.first_name} (id={me.id})")


if __name__ == "__main__":
    import asyncio
    asyncio.run(_smoke_test())
