from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.persistence.models import (
    Inventory,
    StorageLocation,
    StockMovement,
    Warehouse,
    WarehouseZone,
)


class InventoryApplicationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_movement(
        self,
        product_id: int,
        from_location_id: Optional[int],
        to_location_id: Optional[int],
        quantity: int,
        movement_type: str,
        reason: Optional[str],
    ) -> StockMovement:
        movement = StockMovement(
            product_id=product_id,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            quantity=quantity,
            movement_type=movement_type,
            reason=reason,
        )
        self._session.add(movement)

        if from_location_id is not None:
            result = await self._session.execute(
                select(Inventory).where(
                    Inventory.product_id == product_id,
                    Inventory.location_id == from_location_id,
                )
            )
            inv = result.scalar_one_or_none()
            if inv is not None:
                inv.quantity -= quantity

        if to_location_id is not None:
            result = await self._session.execute(
                select(Inventory).where(
                    Inventory.product_id == product_id,
                    Inventory.location_id == to_location_id,
                )
            )
            inv = result.scalar_one_or_none()
            if inv is not None:
                inv.quantity += quantity
            else:
                self._session.add(
                    Inventory(
                        product_id=product_id,
                        location_id=to_location_id,
                        quantity=quantity,
                    )
                )

        await self._session.commit()
        await self._session.refresh(movement)

        return movement

    async def get_total_stock(self, product_id: int) -> Dict[str, int]:
        result = await self._session.execute(
            select(
                func.sum(Inventory.quantity).label("total"),
                func.sum(Inventory.reserved_quantity).label("reserved"),
            ).where(Inventory.product_id == product_id)
        )
        row = result.one()
        total = row.total or 0
        reserved = row.reserved or 0

        return {"total": total, "available": total - reserved, "reserved": reserved}

    async def list_warehouses(self) -> List[Warehouse]:
        result = await self._session.execute(
            select(Warehouse).where(Warehouse.is_active == True)
        )

        return list(result.scalars().all())

    async def list_zones(self) -> List[WarehouseZone]:
        result = await self._session.execute(
            select(WarehouseZone).where(WarehouseZone.is_active == True)
        )

        return list(result.scalars().all())

    async def list_locations(self, zone_id: Optional[int] = None) -> List[StorageLocation]:
        query = select(StorageLocation)
        if zone_id is not None:
            query = query.where(StorageLocation.zone_id == zone_id)
        result = await self._session.execute(query)

        return list(result.scalars().all())

    async def list_inventory(
        self,
        product_id: Optional[int] = None,
        location_id: Optional[int] = None,
    ) -> List[Inventory]:
        query = select(Inventory)
        if product_id is not None:
            query = query.where(Inventory.product_id == product_id)
        if location_id is not None:
            query = query.where(Inventory.location_id == location_id)
        result = await self._session.execute(query)

        return list(result.scalars().all())

    async def list_movements(self, product_id: Optional[int] = None) -> List[StockMovement]:
        query = select(StockMovement).order_by(StockMovement.performed_at.desc())
        if product_id is not None:
            query = query.where(StockMovement.product_id == product_id)
        result = await self._session.execute(query)

        return list(result.scalars().all())
