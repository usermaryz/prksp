from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.warehouse import Warehouse


class WarehouseRepository(ABC):

    @abstractmethod
    async def find_by_id(self, warehouse_id: int) -> Optional[Warehouse]:
        pass

    @abstractmethod
    async def find_all(self, active_only: bool = True) -> List[Warehouse]:
        pass

    @abstractmethod
    async def save(self, warehouse: Warehouse) -> Warehouse:
        pass
