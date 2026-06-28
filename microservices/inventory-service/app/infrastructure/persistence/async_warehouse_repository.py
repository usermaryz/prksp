from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.warehouse import Warehouse as WarehouseDomain
from ...domain.repositories.warehouse_repository import WarehouseRepository
from .models import Warehouse as WarehouseModel


class AsyncWarehouseRepository(WarehouseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, warehouse_id: int) -> Optional[WarehouseDomain]:
        result = await self._session.execute(
            select(WarehouseModel).where(WarehouseModel.id == warehouse_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None

        return self._to_domain(row)

    async def find_all(self, active_only: bool = True) -> List[WarehouseDomain]:
        query = select(WarehouseModel)
        if active_only:
            query = query.where(WarehouseModel.is_active == True)
        result = await self._session.execute(query)

        return [self._to_domain(row) for row in result.scalars().all()]

    async def save(self, warehouse: WarehouseDomain) -> WarehouseDomain:
        if warehouse.id is None:
            model = WarehouseModel(
                code=warehouse.code,
                name=warehouse.name,
                address=warehouse.address,
                is_active=warehouse.is_active,
            )
            self._session.add(model)
            await self._session.flush()
            warehouse.id = model.id
        else:
            result = await self._session.execute(
                select(WarehouseModel).where(WarehouseModel.id == warehouse.id)
            )
            model = result.scalar_one()
            model.code = warehouse.code
            model.name = warehouse.name
            model.address = warehouse.address
            model.is_active = warehouse.is_active

        return warehouse

    def _to_domain(self, model: WarehouseModel) -> WarehouseDomain:
        return WarehouseDomain(
            id=model.id,
            code=model.code,
            name=model.name,
            address=model.address,
            is_active=model.is_active,
            created_at=model.created_at,
        )
