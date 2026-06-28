from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class StorageLocation:
    id: Optional[int]
    zone_id: int
    code: str
    aisle: Optional[str]
    rack: Optional[str]
    shelf: Optional[str]
    bin: Optional[str]
    location_type: str
    is_available: bool
    created_at: datetime = field(default_factory=datetime.utcnow)

    def occupy(self) -> None:
        self.is_available = False

    def vacate(self) -> None:
        self.is_available = True
