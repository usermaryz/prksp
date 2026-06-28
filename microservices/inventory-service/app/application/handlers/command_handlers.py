from __future__ import annotations

from ..commands import CreateMovementCommand, SeedDataCommand
from ..services.inventory_application_service import InventoryApplicationService


async def handle_create_movement(
    cmd: CreateMovementCommand,
    service: InventoryApplicationService,
):
    return await service.create_movement(
        product_id=cmd.product_id,
        from_location_id=cmd.from_location_id,
        to_location_id=cmd.to_location_id,
        quantity=cmd.quantity,
        movement_type=cmd.movement_type,
        reason=cmd.reason,
    )


async def handle_seed_data(
    cmd: SeedDataCommand,
    service: InventoryApplicationService,
) -> None:
    pass
