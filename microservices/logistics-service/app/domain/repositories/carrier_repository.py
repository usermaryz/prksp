from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.carrier import Carrier


class CarrierRepository(ABC):
    @abstractmethod
    def find_by_id(self, carrier_id: int) -> Optional[Carrier]:
        pass

    @abstractmethod
    def find_all_active(self) -> List[Carrier]:
        pass

    @abstractmethod
    def save(self, carrier: Carrier) -> Carrier:
        pass
