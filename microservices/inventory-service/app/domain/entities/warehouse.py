from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Warehouse:
    id: Optional[int]
    code: str
    name: str
    address: Optional[str]
    is_active: bool
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, code: str, name: str, address: Optional[str] = None) -> Warehouse:
        return cls(
            id=None,
            code=code,
            name=name,
            address=address,
            is_active=True,
        )
