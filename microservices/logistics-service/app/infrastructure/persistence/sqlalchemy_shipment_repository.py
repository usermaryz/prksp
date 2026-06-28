from typing import List, Optional
from sqlalchemy.orm import Session

from ...domain.entities.shipment import Shipment
from ...domain.repositories.shipment_repository import ShipmentRepository
from ...domain.value_objects.shipment_status import ShipmentStatus, ShipmentStatusEnum
from .models import ShipmentModel


class SQLAlchemyShipmentRepository(ShipmentRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, shipment_id: int) -> Optional[Shipment]:
        model = self._session.query(ShipmentModel).filter(
            ShipmentModel.id == shipment_id
        ).first()
        if not model:
            return None

        return self._to_entity(model)

    def find_by_order_id(self, order_id: int) -> Optional[Shipment]:
        model = self._session.query(ShipmentModel).filter(
            ShipmentModel.order_id == order_id
        ).first()
        if not model:
            return None

        return self._to_entity(model)

    def find_by_tracking(self, tracking_number: str) -> Optional[Shipment]:
        model = self._session.query(ShipmentModel).filter(
            ShipmentModel.tracking_number == tracking_number
        ).first()
        if not model:
            return None

        return self._to_entity(model)

    def find_all(self, status: Optional[ShipmentStatusEnum] = None) -> List[Shipment]:
        query = self._session.query(ShipmentModel)
        if status:
            query = query.filter(ShipmentModel.status == status.value)
        models = query.order_by(ShipmentModel.created_at.desc()).all()

        return [self._to_entity(m) for m in models]

    def save(self, shipment: Shipment) -> Shipment:
        if shipment.id is None:
            return self._create(shipment)

        return self._update(shipment)

    def count_by_status(self, status: ShipmentStatusEnum) -> int:
        return self._session.query(ShipmentModel).filter(
            ShipmentModel.status == status.value
        ).count()

    def _create(self, shipment: Shipment) -> Shipment:
        model = self._to_model(shipment)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def _update(self, shipment: Shipment) -> Shipment:
        model = self._session.query(ShipmentModel).filter(
            ShipmentModel.id == shipment.id
        ).first()
        if not model:
            raise ValueError(f"Shipment {shipment.id} not found")

        model.order_id = shipment.order_id
        model.order_number = shipment.order_number
        model.tracking_number = shipment.tracking_number
        model.carrier_id = shipment.carrier_id
        model.carrier_name = shipment.carrier_name
        model.delivery_method = shipment.delivery_method
        model.status = shipment.status.value.value
        model.recipient_name = shipment.recipient_name
        model.recipient_phone = shipment.recipient_phone
        model.delivery_address = shipment.delivery_address
        model.estimated_delivery = shipment.estimated_delivery
        model.shipped_at = shipment.shipped_at
        model.delivered_at = shipment.delivered_at

        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def _to_entity(self, model: ShipmentModel) -> Shipment:
        return Shipment(
            id=model.id,
            order_id=model.order_id,
            order_number=model.order_number,
            tracking_number=model.tracking_number,
            carrier_id=model.carrier_id,
            carrier_name=model.carrier_name,
            delivery_method=model.delivery_method or "courier",
            status=ShipmentStatus.from_string(model.status or "pending"),
            recipient_name=model.recipient_name,
            recipient_phone=model.recipient_phone,
            delivery_address=model.delivery_address,
            estimated_delivery=model.estimated_delivery,
            created_at=model.created_at,
            shipped_at=model.shipped_at,
            delivered_at=model.delivered_at,
        )

    def _to_model(self, shipment: Shipment) -> ShipmentModel:
        return ShipmentModel(
            order_id=shipment.order_id,
            order_number=shipment.order_number,
            tracking_number=shipment.tracking_number,
            carrier_id=shipment.carrier_id,
            carrier_name=shipment.carrier_name,
            delivery_method=shipment.delivery_method,
            status=shipment.status.value.value,
            recipient_name=shipment.recipient_name,
            recipient_phone=shipment.recipient_phone,
            delivery_address=shipment.delivery_address,
            estimated_delivery=shipment.estimated_delivery,
            created_at=shipment.created_at,
            shipped_at=shipment.shipped_at,
            delivered_at=shipment.delivered_at,
        )
