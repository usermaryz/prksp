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
class ShipmentCreatedEvent(DomainEvent):
    shipment_id: Optional[int] = None
    order_id: Optional[int] = None
    tracking_number: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {
            "shipment_id": self.shipment_id,
            "order_id": self.order_id,
            "tracking_number": self.tracking_number,
        }


@dataclass
class ShipmentShippedEvent(DomainEvent):
    shipment_id: Optional[int] = None
    order_id: Optional[int] = None

    def _payload(self) -> Dict[str, Any]:
        return {
            "shipment_id": self.shipment_id,
            "order_id": self.order_id,
        }


@dataclass
class ShipmentDeliveredEvent(DomainEvent):
    shipment_id: Optional[int] = None
    order_id: Optional[int] = None

    def _payload(self) -> Dict[str, Any]:
        return {
            "shipment_id": self.shipment_id,
            "order_id": self.order_id,
        }
