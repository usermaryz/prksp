from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class WarehouseZone:
    id: Optional[int]
    warehouse_id: Optional[int]
    code: str
    name: str
    description: Optional[str]
    zone_type: str
    capacity: int
    current_usage: int
    is_active: bool
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def utilization_percent(self) -> float:
        if self.capacity == 0:
            return 0.0

        return round(self.current_usage / self.capacity * 100, 2)

    def add_usage(self, qty: int) -> None:
        if self.current_usage + qty > self.capacity:
            raise ValueError(
                f"Zone {self.code} capacity exceeded: "
                f"current={self.current_usage}, adding={qty}, capacity={self.capacity}"
            )
        self.current_usage += qty

    def remove_usage(self, qty: int) -> None:
        if self.current_usage - qty < 0:
            raise ValueError(
                f"Zone {self.code} usage cannot go below 0: "
                f"current={self.current_usage}, removing={qty}"
            )
        self.current_usage -= qty
