from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.inventory_item import InventoryItem as InventoryItemDomain
from ...domain.repositories.inventory_repository import InventoryRepository
from .models import Inventory as InventoryModel


class AsyncInventoryRepository(InventoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, item_id: int) -> Optional[InventoryItemDomain]:
        result = await self._session.execute(
            select(InventoryModel).where(InventoryModel.id == item_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None

        return self._to_domain(row)

    async def find_all(
        self,
        product_id: Optional[int] = None,
        location_id: Optional[int] = None,
    ) -> List[InventoryItemDomain]:
        query = select(InventoryModel)
        if product_id is not None:
            query = query.where(InventoryModel.product_id == product_id)
        if location_id is not None:
            query = query.where(InventoryModel.location_id == location_id)
        result = await self._session.execute(query)

        return [self._to_domain(row) for row in result.scalars().all()]

    async def save(self, item: InventoryItemDomain) -> InventoryItemDomain:
        if item.id is None:
            model = InventoryModel(
                product_id=item.product_id,
                location_id=item.location_id,
                quantity=item.quantity,
                reserved_quantity=item.reserved_quantity,
                lot_number=item.lot_number,
                expiry_date=item.expiry_date,
            )
            self._session.add(model)
            await self._session.flush()
            item.id = model.id
        else:
            result = await self._session.execute(
                select(InventoryModel).where(InventoryModel.id == item.id)
            )
            model = result.scalar_one()
            model.product_id = item.product_id
            model.location_id = item.location_id
            model.quantity = item.quantity
            model.reserved_quantity = item.reserved_quantity
            model.lot_number = item.lot_number
            model.expiry_date = item.expiry_date

        return item

    def _to_domain(self, model: InventoryModel) -> InventoryItemDomain:
        return InventoryItemDomain(
            id=model.id,
            product_id=model.product_id,
            location_id=model.location_id,
            quantity=model.quantity,
            reserved_quantity=model.reserved_quantity,
            lot_number=model.lot_number,
            expiry_date=model.expiry_date,
            received_at=model.received_at,
        )
