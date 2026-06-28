from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.zone import WarehouseZone


class ZoneRepository(ABC):

    @abstractmethod
    async def find_by_id(self, zone_id: int) -> Optional[WarehouseZone]:
        pass

    @abstractmethod
    async def find_all(self, active_only: bool = True) -> List[WarehouseZone]:
        pass

    @abstractmethod
    async def save(self, zone: WarehouseZone) -> WarehouseZone:
        pass
