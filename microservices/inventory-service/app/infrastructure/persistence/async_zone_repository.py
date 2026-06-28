from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.zone import WarehouseZone as ZoneDomain
from ...domain.repositories.zone_repository import ZoneRepository
from .models import WarehouseZone as ZoneModel


class AsyncZoneRepository(ZoneRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, zone_id: int) -> Optional[ZoneDomain]:
        result = await self._session.execute(
            select(ZoneModel).where(ZoneModel.id == zone_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None

        return self._to_domain(row)

    async def find_all(self, active_only: bool = True) -> List[ZoneDomain]:
        query = select(ZoneModel)
        if active_only:
            query = query.where(ZoneModel.is_active == True)
        result = await self._session.execute(query)

        return [self._to_domain(row) for row in result.scalars().all()]

    async def save(self, zone: ZoneDomain) -> ZoneDomain:
        if zone.id is None:
            model = ZoneModel(
                warehouse_id=zone.warehouse_id,
                code=zone.code,
                name=zone.name,
                description=zone.description,
                zone_type=zone.zone_type,
                capacity=zone.capacity,
                current_usage=zone.current_usage,
                is_active=zone.is_active,
            )
            self._session.add(model)
            await self._session.flush()
            zone.id = model.id
        else:
            result = await self._session.execute(
                select(ZoneModel).where(ZoneModel.id == zone.id)
            )
            model = result.scalar_one()
            model.warehouse_id = zone.warehouse_id
            model.code = zone.code
            model.name = zone.name
            model.description = zone.description
            model.zone_type = zone.zone_type
            model.capacity = zone.capacity
            model.current_usage = zone.current_usage
            model.is_active = zone.is_active

        return zone

    def _to_domain(self, model: ZoneModel) -> ZoneDomain:
        return ZoneDomain(
            id=model.id,
            warehouse_id=model.warehouse_id,
            code=model.code,
            name=model.name,
            description=model.description,
            zone_type=model.zone_type,
            capacity=model.capacity,
            current_usage=model.current_usage,
            is_active=model.is_active,
            created_at=model.created_at,
        )
