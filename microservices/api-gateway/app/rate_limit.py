"""Sliding-window rate limiting backed by Redis (required)."""
from __future__ import annotations

import os
import time

from app.redis_client import get_redis

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
WINDOW_SECONDS = 60


def allow_request(client_key: str) -> tuple[bool, int]:
    """Returns (allowed, retry_after_seconds)."""
    return _allow_redis(get_redis(), client_key)


def _allow_redis(r, client_key: str) -> tuple[bool, int]:
    now = time.time()
    window_start = now - WINDOW_SECONDS
    key = f"rl:{client_key}"
    pipe = r.pipeline()
    pipe.zremrangebyscore(key, "-inf", window_start)
    pipe.zcard(key)
    pipe.zadd(key, {str(now): now})
    pipe.expire(key, WINDOW_SECONDS + 1)
    _, count, _, _ = pipe.execute()
    if count >= RATE_LIMIT_PER_MINUTE:
        oldest_raw = r.zrange(key, 0, 0, withscores=True)
        oldest = oldest_raw[0][1] if oldest_raw else now
        retry_after = max(1, int(WINDOW_SECONDS - (now - oldest)))
        r.zrem(key, str(now))
        return False, retry_after
    return True, 0
