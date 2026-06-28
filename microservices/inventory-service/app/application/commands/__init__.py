from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateMovementCommand:
    product_id: int
    from_location_id: Optional[int]
    to_location_id: Optional[int]
    quantity: int
    movement_type: str
    reason: Optional[str]


@dataclass(frozen=True)
class SeedDataCommand:
    pass
