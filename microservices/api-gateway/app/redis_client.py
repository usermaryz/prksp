"""Mandatory Redis client for API Gateway rate limiting."""
from __future__ import annotations

import redis as _redis

from app.wms_config import require_env

REDIS_URL = require_env("REDIS_URL", "Example: redis://localhost:6379/0")

_client: _redis.Redis | None = None


def get_redis() -> _redis.Redis:
    global _client
    if _client is not None:
        return _client
    client = _redis.from_url(REDIS_URL, socket_connect_timeout=2, socket_timeout=2)
    client.ping()
    _client = client
    return _client


def verify_redis_connection() -> None:
    get_redis()
