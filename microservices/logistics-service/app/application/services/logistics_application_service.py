from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import random

from ...domain.entities.shipment import Shipment
from ...domain.entities.carrier import Carrier
from ...domain.repositories.shipment_repository import ShipmentRepository
from ...domain.repositories.carrier_repository import CarrierRepository
from ...domain.value_objects.shipment_status import ShipmentStatusEnum


@dataclass
class ShipmentDTO:
    id: int
    order_id: int
    order_number: Optional[str]
    tracking_number: str
    carrier_name: Optional[str]
    status: str
    recipient_name: Optional[str]
    delivery_address: Optional[str]
    estimated_delivery: Optional[str]
    created_at: str

    @classmethod
    def from_entity(cls, shipment: Shipment) -> "ShipmentDTO":
        return cls(
            id=shipment.id,
            order_id=shipment.order_id,
            order_number=shipment.order_number,
            tracking_number=shipment.tracking_number,
            carrier_name=shipment.carrier_name,
            status=shipment.status.value.value,
            recipient_name=shipment.recipient_name,
            delivery_address=shipment.delivery_address,
            estimated_delivery=shipment.estimated_delivery,
            created_at=shipment.created_at.isoformat(),
        )


class LogisticsApplicationService:
    def __init__(
        self,
        shipment_repo: ShipmentRepository,
        carrier_repo: CarrierRepository,
    ) -> None:
        self._shipment_repo = shipment_repo
        self._carrier_repo = carrier_repo

    def _generate_tracking(self) -> str:
        return f"WMS{datetime.now().strftime('%y%m%d')}{random.randint(10000, 99999)}"

    def _estimated_delivery(self) -> str:
        return (datetime.now() + timedelta(days=3)).strftime("%d.%m.%Y")

    def create_shipment(
        self,
        order_id: int,
        carrier_id: int,
        delivery_method: str,
    ) -> ShipmentDTO:
        carrier = self._carrier_repo.find_by_id(carrier_id)
        tracking = self._generate_tracking()

        shipment = Shipment.create(
            order_id=order_id,
            order_number=None,
            tracking_number=tracking,
            carrier_id=carrier_id,
            carrier_name=carrier.name if carrier else None,
            recipient_name=None,
            recipient_phone=None,
            delivery_address=None,
            estimated_delivery=self._estimated_delivery(),
            delivery_method=delivery_method,
        )

        saved = self._shipment_repo.save(shipment)

        return ShipmentDTO.from_entity(saved)

    def create_shipment_internal(
        self,
        order_id: int,
        order_number: Optional[str],
        recipient_name: Optional[str],
        recipient_phone: Optional[str],
        delivery_address: Optional[str],
    ) -> ShipmentDTO:
        existing = self._shipment_repo.find_by_order_id(order_id)
        if existing:
            return ShipmentDTO.from_entity(existing)

        carrier = next(iter(self._carrier_repo.find_all_active()), None)
        tracking = self._generate_tracking()

        shipment = Shipment.create(
            order_id=order_id,
            order_number=order_number,
            tracking_number=tracking,
            carrier_id=carrier.id if carrier else None,
            carrier_name=carrier.name if carrier else "СДЭК",
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            delivery_address=delivery_address,
            estimated_delivery=self._estimated_delivery(),
        )

        saved = self._shipment_repo.save(shipment)

        return ShipmentDTO.from_entity(saved)

    def get_shipment(self, shipment_id: int) -> Optional[ShipmentDTO]:
        shipment = self._shipment_repo.find_by_id(shipment_id)
        if not shipment:
            return None

        return ShipmentDTO.from_entity(shipment)

    def list_shipments(self, status: Optional[str] = None) -> List[ShipmentDTO]:
        status_enum = ShipmentStatusEnum(status) if status else None
        shipments = self._shipment_repo.find_all(status=status_enum)

        return [ShipmentDTO.from_entity(s) for s in shipments]

    def list_carriers(self) -> List[Dict[str, Any]]:
        carriers = self._carrier_repo.find_all_active()

        return [{"id": c.id, "code": c.code, "name": c.name} for c in carriers]

    def get_stats(self) -> Dict[str, int]:
        total = sum(
            self._shipment_repo.count_by_status(s) for s in ShipmentStatusEnum
        )

        return {
            "total": total,
            "pending": self._shipment_repo.count_by_status(ShipmentStatusEnum.PENDING),
            "in_transit": self._shipment_repo.count_by_status(ShipmentStatusEnum.IN_TRANSIT),
            "delivered": self._shipment_repo.count_by_status(ShipmentStatusEnum.DELIVERED),
        }
