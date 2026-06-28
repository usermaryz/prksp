from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ListOrdersQuery:
    status: Optional[str] = None
    page: int = 1
    limit: int = 20
