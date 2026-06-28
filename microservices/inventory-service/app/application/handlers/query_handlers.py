from __future__ import annotations

from ..queries import (
    GetStockQuery,
    ListInventoryQuery,
    ListLocationsQuery,
    ListMovementsQuery,
    ListWarehousesQuery,
    ListZonesQuery,
)
from ..services.inventory_application_service import InventoryApplicationService


async def handle_get_stock(
    query: GetStockQuery,
    service: InventoryApplicationService,
):
    return await service.get_total_stock(query.product_id)


async def handle_list_inventory(
    query: ListInventoryQuery,
    service: InventoryApplicationService,
):
    return await service.list_inventory(
        product_id=query.product_id,
        location_id=query.location_id,
    )


async def handle_list_locations(
    query: ListLocationsQuery,
    service: InventoryApplicationService,
):
    return await service.list_locations(zone_id=query.zone_id)


async def handle_list_zones(
    query: ListZonesQuery,
    service: InventoryApplicationService,
):
    return await service.list_zones()


async def handle_list_warehouses(
    query: ListWarehousesQuery,
    service: InventoryApplicationService,
):
    return await service.list_warehouses()


async def handle_list_movements(
    query: ListMovementsQuery,
    service: InventoryApplicationService,
):
    return await service.list_movements(product_id=query.product_id)
