from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.location import StorageLocation as LocationDomain
from ...domain.repositories.location_repository import LocationRepository
from .models import StorageLocation as LocationModel


class AsyncLocationRepository(LocationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, location_id: int) -> Optional[LocationDomain]:
        result = await self._session.execute(
            select(LocationModel).where(LocationModel.id == location_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None

        return self._to_domain(row)

    async def find_all(self, zone_id: Optional[int] = None) -> List[LocationDomain]:
        query = select(LocationModel)
        if zone_id is not None:
            query = query.where(LocationModel.zone_id == zone_id)
        result = await self._session.execute(query)

        return [self._to_domain(row) for row in result.scalars().all()]

    async def save(self, location: LocationDomain) -> LocationDomain:
        if location.id is None:
            model = LocationModel(
                zone_id=location.zone_id,
                code=location.code,
                aisle=location.aisle,
                rack=location.rack,
                shelf=location.shelf,
                bin=location.bin,
                location_type=location.location_type,
                is_available=location.is_available,
            )
            self._session.add(model)
            await self._session.flush()
            location.id = model.id
        else:
            result = await self._session.execute(
                select(LocationModel).where(LocationModel.id == location.id)
            )
            model = result.scalar_one()
            model.zone_id = location.zone_id
            model.code = location.code
            model.aisle = location.aisle
            model.rack = location.rack
            model.shelf = location.shelf
            model.bin = location.bin
            model.location_type = location.location_type
            model.is_available = location.is_available

        return location

    def _to_domain(self, model: LocationModel) -> LocationDomain:
        return LocationDomain(
            id=model.id,
            zone_id=model.zone_id,
            code=model.code,
            aisle=model.aisle,
            rack=model.rack,
            shelf=model.shelf,
            bin=model.bin,
            location_type=model.location_type,
            is_available=model.is_available,
            created_at=model.created_at,
        )
