from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.shipment import Shipment
from ..value_objects.shipment_status import ShipmentStatusEnum


class ShipmentRepository(ABC):
    @abstractmethod
    def find_by_id(self, shipment_id: int) -> Optional[Shipment]:
        pass

    @abstractmethod
    def find_by_order_id(self, order_id: int) -> Optional[Shipment]:
        pass

    @abstractmethod
    def find_by_tracking(self, tracking_number: str) -> Optional[Shipment]:
        pass

    @abstractmethod
    def find_all(self, status: Optional[ShipmentStatusEnum] = None) -> List[Shipment]:
        pass

    @abstractmethod
    def save(self, shipment: Shipment) -> Shipment:
        pass

    @abstractmethod
    def count_by_status(self, status: ShipmentStatusEnum) -> int:
        pass
