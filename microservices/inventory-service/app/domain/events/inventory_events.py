from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


@dataclass
class DomainEvent(ABC):
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def event_name(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "occurred_at": self.occurred_at.isoformat(),
            "payload": self._payload(),
        }

    def _payload(self) -> Dict[str, Any]:
        return {}


@dataclass
class StockMovementCreatedEvent(DomainEvent):
    product_id: Optional[int] = None
    quantity: int = 0
    movement_type: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "movement_type": self.movement_type,
        }


@dataclass
class StockLevelChangedEvent(DomainEvent):
    product_id: Optional[int] = None
    location_id: Optional[int] = None
    new_quantity: int = 0

    def _payload(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "location_id": self.location_id,
            "new_quantity": self.new_quantity,
        }
