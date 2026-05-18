"""In-memory rate limiting (sliding window per client IP)."""
from __future__ import annotations

import os
import time
from collections import defaultdict

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
WINDOW_SECONDS = 60

_buckets: dict[str, list[float]] = defaultdict(list)


def allow_request(client_key: str) -> tuple[bool, int]:
    """
    Returns (allowed, retry_after_seconds).
    client_key: usually IP or IP + path prefix.
    """
    now = time.time()
    window_start = now - WINDOW_SECONDS
    hits = [t for t in _buckets[client_key] if t > window_start]
    if len(hits) >= RATE_LIMIT_PER_MINUTE:
        oldest = min(hits) if hits else now
        retry_after = max(1, int(WINDOW_SECONDS - (now - oldest)))
        return False, retry_after
    hits.append(now)
    _buckets[client_key] = hits
    return True, 0
