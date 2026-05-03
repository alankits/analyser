"""Cache helpers for Redis. All operations are no-ops when Redis is not configured."""

from __future__ import annotations

import json
import logging
from typing import Any

from core.config import settings

logger = logging.getLogger(__name__)

_redis_client: Any = None
_CACHE_TTL_SECONDS = 3600  # 1 hour


async def _get_client() -> Any:
    """Return a connected Redis client, or None if Redis is disabled/unavailable."""
    global _redis_client
    if not settings.redis_enabled:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        import aioredis  # type: ignore

        _redis_client = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("Redis connected: %s", settings.redis_url)
        return _redis_client
    except Exception as exc:
        logger.warning("Redis unavailable, caching disabled: %s", exc)
        return None


async def cache_get(key: str) -> Any | None:
    """Return cached value or None if not found / Redis unavailable."""
    client = await _get_client()
    if client is None:
        return None
    try:
        raw = await client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Cache read error for key=%s: %s", key, exc)
        return None


async def cache_set(key: str, value: Any) -> None:
    """Store value in Redis with TTL. Silently skips if Redis unavailable."""
    client = await _get_client()
    if client is None:
        return
    try:
        await client.set(key, json.dumps(value), ex=_CACHE_TTL_SECONDS)
    except Exception as exc:
        logger.warning("Cache write error for key=%s: %s", key, exc)


async def cache_ping() -> bool:
    """Return True if Redis is reachable."""
    client = await _get_client()
    if client is None:
        return False
    try:
        return await client.ping()
    except Exception:
        return False
