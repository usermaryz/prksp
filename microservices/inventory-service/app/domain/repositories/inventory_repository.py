from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.inventory_item import InventoryItem


class InventoryRepository(ABC):

    @abstractmethod
    async def find_by_id(self, item_id: int) -> Optional[InventoryItem]:
        pass

    @abstractmethod
    async def find_all(
        self,
        product_id: Optional[int] = None,
        location_id: Optional[int] = None,
    ) -> List[InventoryItem]:
        pass

    @abstractmethod
    async def save(self, item: InventoryItem) -> InventoryItem:
        pass
