"""Env helpers (kept in sync across microservices)."""
from __future__ import annotations

import os


def require_env(name: str, hint: str = "") -> str:
    val = os.getenv(name, "").strip()
    if not val:
        msg = f"{name} environment variable is not set."
        if hint:
            msg += f" {hint}"
        raise RuntimeError(msg)
    return val


def env_or_empty(name: str) -> str:
    return os.getenv(name, "").strip()
