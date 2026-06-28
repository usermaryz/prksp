from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ..value_objects.shipment_status import ShipmentStatus, ShipmentStatusEnum
from ..events.shipment_events import DomainEvent, ShipmentCreatedEvent, ShipmentShippedEvent, ShipmentDeliveredEvent


@dataclass
class Shipment:
    id: Optional[int]
    order_id: int
    order_number: Optional[str]
    tracking_number: str
    carrier_id: Optional[int]
    carrier_name: Optional[str]
    delivery_method: str
    status: ShipmentStatus
    recipient_name: Optional[str]
    recipient_phone: Optional[str]
    delivery_address: Optional[str]
    estimated_delivery: Optional[str]
    created_at: datetime
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    _domain_events: List[DomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        order_id: int,
        order_number: Optional[str],
        tracking_number: str,
        carrier_id: Optional[int],
        carrier_name: Optional[str],
        recipient_name: Optional[str],
        recipient_phone: Optional[str],
        delivery_address: Optional[str],
        estimated_delivery: Optional[str],
        delivery_method: str = "courier",
    ) -> "Shipment":
        shipment = cls(
            id=None,
            order_id=order_id,
            order_number=order_number,
            tracking_number=tracking_number,
            carrier_id=carrier_id,
            carrier_name=carrier_name,
            delivery_method=delivery_method,
            status=ShipmentStatus.initial(),
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            delivery_address=delivery_address,
            estimated_delivery=estimated_delivery,
            created_at=datetime.utcnow(),
        )
        shipment._domain_events.append(
            ShipmentCreatedEvent(
                shipment_id=None,
                order_id=order_id,
                tracking_number=tracking_number,
            )
        )

        return shipment

    def ship(self) -> None:
        self.status = self.status.transition_to(ShipmentStatusEnum.IN_TRANSIT)
        self.shipped_at = datetime.utcnow()
        self._domain_events.append(
            ShipmentShippedEvent(shipment_id=self.id, order_id=self.order_id)
        )

    def deliver(self) -> None:
        self.status = self.status.transition_to(ShipmentStatusEnum.DELIVERED)
        self.delivered_at = datetime.utcnow()
        self._domain_events.append(
            ShipmentDeliveredEvent(shipment_id=self.id, order_id=self.order_id)
        )

    def fail_delivery(self) -> None:
        self.status = self.status.transition_to(ShipmentStatusEnum.FAILED)

    def return_shipment(self) -> None:
        self.status = self.status.transition_to(ShipmentStatusEnum.RETURNED)

    def collect_events(self) -> List[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()

        return events

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shipment):
            return False
        if self.id and other.id:
            return self.id == other.id

        return self.tracking_number == other.tracking_number

    def __hash__(self) -> int:
        return hash(self.tracking_number)
