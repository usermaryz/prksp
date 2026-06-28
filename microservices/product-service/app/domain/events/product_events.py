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
class ProductCreatedEvent(DomainEvent):
    product_id: Optional[int] = None
    sku: str = ""
    name: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "sku": self.sku,
            "name": self.name,
        }


@dataclass
class StockReservedEvent(DomainEvent):
    product_id: Optional[int] = None
    quantity: int = 0

    def _payload(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
        }


@dataclass
class StockReleasedEvent(DomainEvent):
    product_id: Optional[int] = None
    quantity: int = 0

    def _payload(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
        }
