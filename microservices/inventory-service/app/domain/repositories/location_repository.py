from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.location import StorageLocation


class LocationRepository(ABC):

    @abstractmethod
    async def find_by_id(self, location_id: int) -> Optional[StorageLocation]:
        pass

    @abstractmethod
    async def find_all(self, zone_id: Optional[int] = None) -> List[StorageLocation]:
        pass

    @abstractmethod
    async def save(self, location: StorageLocation) -> StorageLocation:
        pass
