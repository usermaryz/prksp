from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ChangeStatusCommand:
    order_id: int
    new_status: str
    reason: Optional[str] = None
