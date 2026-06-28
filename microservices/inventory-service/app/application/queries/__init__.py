from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GetStockQuery:
    product_id: int


@dataclass(frozen=True)
class ListInventoryQuery:
    product_id: Optional[int] = None
    location_id: Optional[int] = None


@dataclass(frozen=True)
class ListLocationsQuery:
    zone_id: Optional[int] = None


@dataclass(frozen=True)
class ListZonesQuery:
    pass


@dataclass(frozen=True)
class ListWarehousesQuery:
    pass


@dataclass(frozen=True)
class ListMovementsQuery:
    product_id: Optional[int] = None
