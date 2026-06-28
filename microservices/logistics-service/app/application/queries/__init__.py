from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GetShipmentQuery:
    shipment_id: int


@dataclass(frozen=True)
class ListShipmentsQuery:
    status: Optional[str] = None


@dataclass(frozen=True)
class ListCarriersQuery:
    pass


@dataclass(frozen=True)
class GetStatsQuery:
    pass
