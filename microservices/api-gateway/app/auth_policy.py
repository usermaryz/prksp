"""RBAC rules for API Gateway (path + method → allowed roles)."""
from __future__ import annotations

import re
from typing import Optional

# (method, path regex, allowed roles). None = any authenticated user.
_ROUTE_RULES: list[tuple[str, re.Pattern[str], Optional[set[str]]]] = [
    ("POST", re.compile(r"^/api/products/?$"), {"admin", "manager"}),
    ("PATCH", re.compile(r"^/api/products/\d+/?$"), {"admin", "manager", "picker"}),
    ("DELETE", re.compile(r"^/api/products/\d+/?$"), {"admin", "manager"}),
    ("POST", re.compile(r"^/api/orders/?$"), {"admin", "manager"}),
    ("PATCH", re.compile(r"^/api/orders/\d+/status/?$"), {"admin", "manager", "picker"}),
    ("POST", re.compile(r"^/api/picking/tasks/\d+/start/?$"), {"admin", "manager", "picker"}),
    ("POST", re.compile(r"^/api/picking/tasks/\d+/complete/?$"), {"admin", "manager", "picker"}),
    ("POST", re.compile(r"^/api/logistics/shipments/?$"), {"admin", "manager"}),
    ("POST", re.compile(r"^/api/inventory/movements/?$"), {"admin", "manager", "picker"}),
]

PUBLIC_PREFIXES = (
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/refresh",
    "/health",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
    "/docs",
    "/redoc",
    "/openapi.json",
)


def is_public_path(path: str) -> bool:
    if path == "/api" or path == "/api/":
        return True
    return any(path == p or path.startswith(p + "/") or path.startswith(p) for p in PUBLIC_PREFIXES)


def required_roles(method: str, path: str) -> Optional[set[str]]:
    """None → любой аутентифицированный пользователь."""
    for rule_method, pattern, roles in _ROUTE_RULES:
        if rule_method == method.upper() and pattern.match(path):
            return roles
    if path.startswith("/api/"):
        return None
    return None
