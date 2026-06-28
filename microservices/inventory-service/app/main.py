"""
Inventory Service — DDD + CQRS + Redis architecture.

Layers:
  domain/         — Entities, Value Objects, Domain Events, Repository ABCs
  application/    — Commands, Queries, Handlers, AsyncCommandBus, AsyncQueryBus
  infrastructure/ — SQLAlchemy async repositories, Redis client
  main.py         — FastAPI endpoints (thin adapter)
"""

import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .application.bus import AsyncCommandBus, AsyncQueryBus
from .application.commands import CreateMovementCommand, SeedDataCommand
from .application.handlers.command_handlers import (
    handle_create_movement,
    handle_seed_data,
)
from .application.handlers.query_handlers import (
    handle_get_stock,
    handle_list_inventory,
    handle_list_locations,
    handle_list_movements,
    handle_list_warehouses,
    handle_list_zones,
)
from .application.queries import (
    GetStockQuery,
    ListInventoryQuery,
    ListLocationsQuery,
    ListMovementsQuery,
    ListWarehousesQuery,
    ListZonesQuery,
)
from .application.services.inventory_application_service import (
    InventoryApplicationService,
)
from .infrastructure.persistence.models import (
    Base,
    Inventory,
    StorageLocation,
    Warehouse,
    WarehouseZone,
)
from .infrastructure.redis_client import get_redis, verify_redis_connection


# =============================================================================
# CONFIG
# =============================================================================
def _default_sqlite_url() -> str:
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "inventory.db")
    )

    return f"sqlite+aiosqlite:///{path}"


class Settings(BaseSettings):
    DATABASE_URL: str = _default_sqlite_url()
    SERVICE_NAME: str = "inventory-service"
    SERVICE_PORT: int = 8004

    class Config:
        env_file = ".env"


settings = Settings()


def _normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return url


_db_url = _normalize_db_url(settings.DATABASE_URL)
_engine_kwargs = {}
if _db_url.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
engine = create_async_engine(_db_url, echo=False, **_engine_kwargs)
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================
class WarehouseResponse(BaseModel):
    id: int
    code: str
    name: str
    address: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class ZoneResponse(BaseModel):
    id: int
    code: str
    name: str
    zone_type: str
    capacity: int
    current_usage: int
    is_active: bool

    class Config:
        from_attributes = True


class LocationResponse(BaseModel):
    id: int
    zone_id: int
    code: str
    aisle: Optional[str]
    rack: Optional[str]
    shelf: Optional[str]
    bin: Optional[str]
    location_type: str
    is_available: bool

    class Config:
        from_attributes = True


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    location_id: int
    quantity: int
    reserved_quantity: int
    lot_number: Optional[str]
    received_at: datetime

    class Config:
        from_attributes = True


class MovementCreate(BaseModel):
    product_id: int
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    quantity: int
    movement_type: str
    reason: Optional[str] = None


class MovementResponse(BaseModel):
    id: int
    product_id: int
    from_location_id: Optional[int]
    to_location_id: Optional[int]
    quantity: int
    movement_type: Optional[str]
    reason: Optional[str]
    performed_by: Optional[int]
    performed_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================
async def get_db():
    async with async_session() as session:
        yield session


async def get_inventory_service(
    db: AsyncSession = Depends(get_db),
) -> InventoryApplicationService:
    return InventoryApplicationService(session=db)


async def get_command_bus(
    service: InventoryApplicationService = Depends(get_inventory_service),
) -> AsyncCommandBus:
    bus = AsyncCommandBus()
    bus.register(
        CreateMovementCommand,
        lambda cmd: handle_create_movement(cmd, service),
    )
    bus.register(SeedDataCommand, lambda cmd: handle_seed_data(cmd, service))

    return bus


async def get_query_bus(
    service: InventoryApplicationService = Depends(get_inventory_service),
) -> AsyncQueryBus:
    bus = AsyncQueryBus()
    bus.register(GetStockQuery, lambda q: handle_get_stock(q, service))
    bus.register(
        ListInventoryQuery, lambda q: handle_list_inventory(q, service)
    )
    bus.register(
        ListLocationsQuery, lambda q: handle_list_locations(q, service)
    )
    bus.register(ListZonesQuery, lambda q: handle_list_zones(q, service))
    bus.register(
        ListWarehousesQuery, lambda q: handle_list_warehouses(q, service)
    )
    bus.register(
        ListMovementsQuery, lambda q: handle_list_movements(q, service)
    )

    return bus


# =============================================================================
# INIT / SEED
# =============================================================================
async def init_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        wh_count = await session.scalar(
            select(func.count()).select_from(Warehouse)
        )
        if wh_count != 0:
            return

        print(f"[{settings.SERVICE_NAME}] Seeding initial data...")
        wh = Warehouse(
            code="WH-01", name="Центральный склад", address="г. Москва"
        )
        session.add(wh)
        await session.flush()
        session.add_all(
            [
                WarehouseZone(
                    warehouse_id=wh.id,
                    code="A",
                    name="Зона A",
                    zone_type="storage",
                    capacity=1000,
                ),
                WarehouseZone(
                    warehouse_id=wh.id,
                    code="B",
                    name="Зона B",
                    zone_type="storage",
                    capacity=800,
                ),
                WarehouseZone(
                    warehouse_id=wh.id,
                    code="C",
                    name="Зона C",
                    zone_type="storage",
                    capacity=600,
                ),
                WarehouseZone(
                    warehouse_id=wh.id,
                    code="R",
                    name="Зона приёмки",
                    zone_type="receiving",
                    capacity=200,
                ),
            ]
        )
        await session.flush()
        zones_result = await session.execute(
            select(WarehouseZone).where(WarehouseZone.warehouse_id == wh.id)
        )
        zones = {z.code: z for z in zones_result.scalars().all()}
        locations = [
            StorageLocation(
                zone_id=zones["A"].id,
                code="A-01-01",
                aisle="1",
                rack="1",
                shelf="1",
            ),
            StorageLocation(
                zone_id=zones["A"].id,
                code="A-01-03",
                aisle="1",
                rack="1",
                shelf="3",
            ),
            StorageLocation(
                zone_id=zones["A"].id,
                code="A-02-01",
                aisle="2",
                rack="1",
                shelf="1",
            ),
            StorageLocation(
                zone_id=zones["B"].id,
                code="B-01-01",
                aisle="1",
                rack="1",
                shelf="1",
            ),
            StorageLocation(
                zone_id=zones["B"].id,
                code="B-02-01",
                aisle="2",
                rack="1",
                shelf="1",
            ),
            StorageLocation(
                zone_id=zones["C"].id,
                code="C-01-01",
                aisle="1",
                rack="1",
                shelf="1",
            ),
            StorageLocation(
                zone_id=zones["C"].id,
                code="C-02-01",
                aisle="2",
                rack="1",
                shelf="1",
            ),
            StorageLocation(
                zone_id=zones["R"].id,
                code="R-01-01",
                aisle="1",
                rack="1",
                shelf="1",
            ),
        ]
        session.add_all(locations)
        await session.flush()
        loc_by_code = {loc.code: loc for loc in locations}
        session.add_all(
            [
                Inventory(
                    product_id=1,
                    location_id=loc_by_code["A-01-03"].id,
                    quantity=45,
                    reserved_quantity=2,
                ),
                Inventory(
                    product_id=2,
                    location_id=loc_by_code["A-01-01"].id,
                    quantity=32,
                    reserved_quantity=0,
                ),
                Inventory(
                    product_id=3,
                    location_id=loc_by_code["A-02-01"].id,
                    quantity=18,
                    reserved_quantity=1,
                ),
                Inventory(
                    product_id=4,
                    location_id=loc_by_code["B-01-01"].id,
                    quantity=12,
                    reserved_quantity=3,
                ),
                Inventory(
                    product_id=5,
                    location_id=loc_by_code["A-01-03"].id,
                    quantity=28,
                    reserved_quantity=0,
                ),
                Inventory(
                    product_id=6,
                    location_id=loc_by_code["A-02-01"].id,
                    quantity=56,
                    reserved_quantity=4,
                ),
                Inventory(
                    product_id=7,
                    location_id=loc_by_code["B-02-01"].id,
                    quantity=8,
                    reserved_quantity=2,
                ),
                Inventory(
                    product_id=8,
                    location_id=loc_by_code["B-01-01"].id,
                    quantity=24,
                    reserved_quantity=0,
                ),
                Inventory(
                    product_id=9,
                    location_id=loc_by_code["A-02-01"].id,
                    quantity=15,
                    reserved_quantity=0,
                ),
                Inventory(
                    product_id=10,
                    location_id=loc_by_code["C-01-01"].id,
                    quantity=40,
                    reserved_quantity=5,
                ),
                Inventory(
                    product_id=11,
                    location_id=loc_by_code["B-02-01"].id,
                    quantity=6,
                    reserved_quantity=1,
                ),
                Inventory(
                    product_id=12,
                    location_id=loc_by_code["C-01-01"].id,
                    quantity=3,
                    reserved_quantity=0,
                ),
                Inventory(
                    product_id=1,
                    location_id=loc_by_code["R-01-01"].id,
                    quantity=5,
                    reserved_quantity=0,
                ),
            ]
        )
        zones["A"].current_usage = 650
        zones["B"].current_usage = 420
        zones["C"].current_usage = 180
        zones["R"].current_usage = 40
        await session.commit()
        print(f"[{settings.SERVICE_NAME}] Demo inventory seeded")


# =============================================================================
# APP
# =============================================================================
@asynccontextmanager
async def lifespan(_: FastAPI):
    print(
        f"[{settings.SERVICE_NAME}] Starting on port "
        f"{settings.SERVICE_PORT} (DDD+CQRS+Redis)..."
    )
    verify_redis_connection()
    await init_database()
    yield
    print(f"[{settings.SERVICE_NAME}] Shutting down...")


app = FastAPI(
    title="Inventory Service (DDD + CQRS)",
    description="""
Микросервис управления складскими остатками WMS.

## Архитектура DDD + CQRS + Redis

- **Domain Layer**: Warehouse, WarehouseZone, StorageLocation,
  InventoryItem (Entities), MovementType (Value Object)
- **Application Layer**: AsyncCommandBus / AsyncQueryBus, Commands,
  Queries, Handlers, InventoryApplicationService
- **Infrastructure Layer**: Async SQLAlchemy repositories, Redis cache
""",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ENDPOINTS
# =============================================================================
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "architecture": "DDD+CQRS+Redis",
    }


@app.get("/warehouses", response_model=List[WarehouseResponse])
async def get_warehouses(
    query_bus: AsyncQueryBus = Depends(get_query_bus),
):
    rows = await query_bus.ask(ListWarehousesQuery())

    return [WarehouseResponse.model_validate(r) for r in rows]


@app.get("/zones", response_model=List[ZoneResponse])
async def get_zones(
    query_bus: AsyncQueryBus = Depends(get_query_bus),
):
    r = get_redis()
    cache_key = "inventory:zones"
    cached = r.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    rows = await query_bus.ask(ListZonesQuery())
    result = [ZoneResponse.model_validate(z) for z in rows]
    r.setex(cache_key, 60, json.dumps([z.model_dump() for z in result]))

    return result


@app.get("/locations", response_model=List[LocationResponse])
async def get_locations(
    zone_id: Optional[int] = None,
    query_bus: AsyncQueryBus = Depends(get_query_bus),
):
    rows = await query_bus.ask(ListLocationsQuery(zone_id=zone_id))

    return [LocationResponse.model_validate(loc) for loc in rows]


@app.get("/inventory", response_model=List[InventoryResponse])
async def get_inventory(
    product_id: Optional[int] = None,
    location_id: Optional[int] = None,
    query_bus: AsyncQueryBus = Depends(get_query_bus),
):
    rows = await query_bus.ask(
        ListInventoryQuery(
            product_id=product_id, location_id=location_id
        )
    )

    return [InventoryResponse.model_validate(i) for i in rows]


@app.get("/inventory/products/{product_id}/stock")
async def get_product_stock(
    product_id: int,
    query_bus: AsyncQueryBus = Depends(get_query_bus),
):
    r = get_redis()
    cache_key = f"inventory:stock:{product_id}"
    cached = r.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    result = await query_bus.ask(GetStockQuery(product_id=product_id))
    r.setex(cache_key, 30, json.dumps(result))

    return result


@app.get("/movements", response_model=List[MovementResponse])
async def list_movements(
    product_id: Optional[int] = None,
    query_bus: AsyncQueryBus = Depends(get_query_bus),
):
    rows = await query_bus.ask(ListMovementsQuery(product_id=product_id))
    return [MovementResponse.model_validate(m) for m in rows]


@app.post("/movements")
async def create_movement(
    data: MovementCreate,
    command_bus: AsyncCommandBus = Depends(get_command_bus),
):
    cmd = CreateMovementCommand(
        product_id=data.product_id,
        from_location_id=data.from_location_id,
        to_location_id=data.to_location_id,
        quantity=data.quantity,
        movement_type=data.movement_type,
        reason=data.reason,
    )
    try:
        await command_bus.dispatch(cmd)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    r = get_redis()
    r.delete("inventory:zones")
    r.delete(f"inventory:stock:{data.product_id}")

    return {"message": "Movement created"}


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
