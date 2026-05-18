"""
Inventory Microservice - Управление складскими остатками
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Date, select, func


def _default_sqlite_url() -> str:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "inventory.db"))
    return f"sqlite+aiosqlite:///{path}"


class Settings(BaseSettings):
    # Локально по умолчанию SQLite (без Docker/PostgreSQL). Для Docker задайте DATABASE_URL в env.
    DATABASE_URL: str = _default_sqlite_url()
    SERVICE_NAME: str = "inventory-service"
    SERVICE_PORT: int = 8004
    class Config:
        env_file = ".env"

settings = Settings()
_engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
engine = create_async_engine(settings.DATABASE_URL, echo=False, **_engine_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WarehouseZone(Base):
    __tablename__ = "warehouse_zones"
    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String)
    zone_type = Column(String(20), default="storage")
    capacity = Column(Integer, default=1000)
    current_usage = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StorageLocation(Base):
    __tablename__ = "storage_locations"
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("warehouse_zones.id"))
    code = Column(String(20), unique=True, nullable=False)
    aisle = Column(String(10))
    rack = Column(String(10))
    shelf = Column(String(10))
    bin = Column(String(10))
    location_type = Column(String(20), default="bulk")
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    location_id = Column(Integer, ForeignKey("storage_locations.id"))
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    lot_number = Column(String(50))
    expiry_date = Column(Date)
    received_at = Column(DateTime, default=datetime.utcnow)
    last_counted_at = Column(DateTime)


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    from_location_id = Column(Integer, ForeignKey("storage_locations.id"))
    to_location_id = Column(Integer, ForeignKey("storage_locations.id"))
    quantity = Column(Integer, nullable=False)
    movement_type = Column(String(20))
    reason = Column(String)
    performed_by = Column(Integer)
    performed_at = Column(DateTime, default=datetime.utcnow)


async def get_db():
    async with async_session() as session:
        yield session


class WarehouseResponse(BaseModel):
    id: int
    code: str
    name: str
    address: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# Schemas
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        wh_count = await session.scalar(select(func.count()).select_from(Warehouse))
        if wh_count == 0:
            wh = Warehouse(code="WH-01", name="Центральный склад", address="г. Москва")
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
                StorageLocation(zone_id=zones["A"].id, code="A-01-01", aisle="1", rack="1", shelf="1"),
                StorageLocation(zone_id=zones["A"].id, code="A-01-03", aisle="1", rack="1", shelf="3"),
                StorageLocation(zone_id=zones["A"].id, code="A-02-01", aisle="2", rack="1", shelf="1"),
                StorageLocation(zone_id=zones["B"].id, code="B-01-01", aisle="1", rack="1", shelf="1"),
                StorageLocation(zone_id=zones["B"].id, code="B-02-01", aisle="2", rack="1", shelf="1"),
                StorageLocation(zone_id=zones["C"].id, code="C-01-01", aisle="1", rack="1", shelf="1"),
                StorageLocation(zone_id=zones["C"].id, code="C-02-01", aisle="2", rack="1", shelf="1"),
                StorageLocation(zone_id=zones["R"].id, code="R-01-01", aisle="1", rack="1", shelf="1"),
            ]
            session.add_all(locations)
            await session.flush()
            loc_by_code = {loc.code: loc for loc in locations}
            session.add_all(
                [
                    Inventory(product_id=1, location_id=loc_by_code["A-01-03"].id, quantity=45, reserved_quantity=2),
                    Inventory(product_id=2, location_id=loc_by_code["A-01-01"].id, quantity=32, reserved_quantity=0),
                    Inventory(product_id=3, location_id=loc_by_code["A-02-01"].id, quantity=18, reserved_quantity=1),
                    Inventory(product_id=4, location_id=loc_by_code["B-01-01"].id, quantity=12, reserved_quantity=3),
                    Inventory(product_id=5, location_id=loc_by_code["A-01-03"].id, quantity=28, reserved_quantity=0),
                    Inventory(product_id=6, location_id=loc_by_code["A-02-01"].id, quantity=56, reserved_quantity=4),
                    Inventory(product_id=7, location_id=loc_by_code["B-02-01"].id, quantity=8, reserved_quantity=2),
                    Inventory(product_id=8, location_id=loc_by_code["B-01-01"].id, quantity=24, reserved_quantity=0),
                    Inventory(product_id=9, location_id=loc_by_code["A-02-01"].id, quantity=15, reserved_quantity=0),
                    Inventory(product_id=10, location_id=loc_by_code["C-01-01"].id, quantity=40, reserved_quantity=5),
                    Inventory(product_id=11, location_id=loc_by_code["B-02-01"].id, quantity=6, reserved_quantity=1),
                    Inventory(product_id=12, location_id=loc_by_code["C-01-01"].id, quantity=3, reserved_quantity=0),
                    Inventory(product_id=1, location_id=loc_by_code["R-01-01"].id, quantity=5, reserved_quantity=0),
                ]
            )
            zones["A"].current_usage = 650
            zones["B"].current_usage = 420
            zones["C"].current_usage = 180
            zones["R"].current_usage = 40
            await session.commit()
            print(f"[{settings.SERVICE_NAME}] Demo inventory seeded")
    yield
    print(f"👋 Shutting down {settings.SERVICE_NAME}...")

app = FastAPI(title="Inventory Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.SERVICE_NAME}


@app.get("/warehouses", response_model=List[WarehouseResponse])
async def get_warehouses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Warehouse).where(Warehouse.is_active == True))
    return [WarehouseResponse.model_validate(w) for w in result.scalars().all()]


@app.get("/zones", response_model=List[ZoneResponse])
async def get_zones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WarehouseZone).where(WarehouseZone.is_active == True))
    zones = result.scalars().all()
    return [ZoneResponse.model_validate(z) for z in zones]


@app.get("/locations", response_model=List[LocationResponse])
async def get_locations(zone_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    query = select(StorageLocation)
    if zone_id:
        query = query.where(StorageLocation.zone_id == zone_id)
    result = await db.execute(query)
    locations = result.scalars().all()
    return [LocationResponse.model_validate(l) for l in locations]


@app.get("/inventory", response_model=List[InventoryResponse])
async def get_inventory(product_id: Optional[int] = None, location_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    query = select(Inventory)
    if product_id:
        query = query.where(Inventory.product_id == product_id)
    if location_id:
        query = query.where(Inventory.location_id == location_id)
    result = await db.execute(query)
    items = result.scalars().all()
    return [InventoryResponse.model_validate(i) for i in items]


@app.get("/inventory/products/{product_id}/stock")
async def get_product_stock(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            func.sum(Inventory.quantity).label("total"),
            func.sum(Inventory.reserved_quantity).label("reserved")
        ).where(Inventory.product_id == product_id)
    )
    row = result.one()
    total = row.total or 0
    reserved = row.reserved or 0
    return {"total": total, "available": total - reserved, "reserved": reserved}


@app.get("/movements", response_model=List[MovementResponse])
async def list_movements(
    product_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(StockMovement).order_by(StockMovement.performed_at.desc())
    if product_id is not None:
        q = q.where(StockMovement.product_id == product_id)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [MovementResponse.model_validate(m) for m in rows]


@app.post("/movements")
async def create_movement(data: MovementCreate, db: AsyncSession = Depends(get_db)):
    movement = StockMovement(**data.model_dump())
    db.add(movement)
    
    # Update inventory
    if data.from_location_id:
        result = await db.execute(
            select(Inventory).where(
                Inventory.product_id == data.product_id,
                Inventory.location_id == data.from_location_id
            )
        )
        inv = result.scalar_one_or_none()
        if inv:
            inv.quantity -= data.quantity
    
    if data.to_location_id:
        result = await db.execute(
            select(Inventory).where(
                Inventory.product_id == data.product_id,
                Inventory.location_id == data.to_location_id
            )
        )
        inv = result.scalar_one_or_none()
        if inv:
            inv.quantity += data.quantity
        else:
            new_inv = Inventory(product_id=data.product_id, location_id=data.to_location_id, quantity=data.quantity)
            db.add(new_inv)
    
    await db.commit()
    return {"message": "Movement created"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)

