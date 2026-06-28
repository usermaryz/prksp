from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..queries import GetShipmentQuery, ListShipmentsQuery, ListCarriersQuery, GetStatsQuery
from ..services.logistics_application_service import LogisticsApplicationService, ShipmentDTO


def handle_get_shipment(
    query: GetShipmentQuery,
    service: LogisticsApplicationService,
) -> Optional[ShipmentDTO]:
    return service.get_shipment(query.shipment_id)


def handle_list_shipments(
    query: ListShipmentsQuery,
    service: LogisticsApplicationService,
) -> List[ShipmentDTO]:
    return service.list_shipments(status=query.status)


def handle_list_carriers(
    query: ListCarriersQuery,
    service: LogisticsApplicationService,
) -> List[Dict[str, Any]]:
    return service.list_carriers()


def handle_get_stats(
    query: GetStatsQuery,
    service: LogisticsApplicationService,
) -> Dict[str, int]:
    return service.get_stats()
