"""
Product Service — DDD + CQRS + Redis architecture.

Layers:
  domain/         — Product (Aggregate Root), Price & ProductStatus (Value Objects), Domain Events
  application/    — CommandBus / QueryBus, Commands, Queries, Handlers, ProductApplicationService
  infrastructure/ — SQLAlchemyProductRepository, RedisClient
  main.py         — FastAPI endpoints (thin adapter)
"""

from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import json
import os

from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .application.bus import CommandBus, QueryBus
from .application.commands import (
    CreateProductCommand,
    DeleteProductCommand,
    ReserveStockCommand,
    ReleaseStockCommand,
    UpdateProductCommand,
)
from .application.queries import GetProductQuery, ListCategoriesQuery, ListProductsQuery, ListZonesQuery
from .application.handlers.command_handlers import (
    handle_create_product,
    handle_delete_product,
    handle_reserve_stock,
    handle_release_stock,
    handle_update_product,
)
from .application.handlers.query_handlers import (
    handle_get_product,
    handle_list_products,
    handle_list_categories,
    handle_list_zones,
)
from .application.services import ProductApplicationService
from .application.services.catalog_query_service import CatalogQueryService
from .infrastructure.persistence import Base, SQLAlchemyProductRepository, CategoryModel, WarehouseZoneModel
from .infrastructure.redis_client import get_redis, verify_redis_connection
from .wms_config import require_env


# =============================================================================
# CONFIG
# =============================================================================
SERVICE_NAME = "product-service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8002"))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "products.db")


def _sync_db_url(raw: str, fallback: str) -> str:
    if not raw:
        return fallback
    raw = raw.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if raw.startswith("postgres://"):
        raw = "postgresql+psycopg2://" + raw[len("postgres://"):]

    return raw


DATABASE_URL = _sync_db_url(
    os.getenv("DATABASE_URL", "").strip(),
    f"sqlite:///{DATABASE_PATH}",
)
INTERNAL_API_KEY = require_env(
    "INTERNAL_API_KEY",
    "Generate with: openssl rand -hex 32",
)

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    location: Optional[str] = None
    status: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    sku: str
    barcode: str
    name: str
    description: Optional[str]
    price: Optional[Decimal]
    stock: int
    reserved: int
    location: Optional[str]
    status: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReserveItem(BaseModel):
    product_id: int
    quantity: int


class ReserveRequest(BaseModel):
    items: List[ReserveItem]


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_product_service(db: Session = Depends(get_db)) -> ProductApplicationService:
    repository = SQLAlchemyProductRepository(db)

    return ProductApplicationService(repository=repository)


def get_command_bus(service: ProductApplicationService = Depends(get_product_service)) -> CommandBus:
    bus = CommandBus()
    bus.register(CreateProductCommand, lambda cmd: handle_create_product(cmd, service))
    bus.register(DeleteProductCommand, lambda cmd: handle_delete_product(cmd, service))
    bus.register(ReserveStockCommand, lambda cmd: handle_reserve_stock(cmd, service))
    bus.register(ReleaseStockCommand, lambda cmd: handle_release_stock(cmd, service))
    bus.register(UpdateProductCommand, lambda cmd: handle_update_product(cmd, service))

    return bus


def get_catalog_service(db: Session = Depends(get_db)) -> CatalogQueryService:
    return CatalogQueryService(db)


def get_query_bus(
    service: ProductApplicationService = Depends(get_product_service),
    catalog: CatalogQueryService = Depends(get_catalog_service),
) -> QueryBus:
    bus = QueryBus()
    bus.register(GetProductQuery, lambda q: handle_get_product(q, service))
    bus.register(ListProductsQuery, lambda q: handle_list_products(q, service))
    bus.register(ListCategoriesQuery, lambda q: handle_list_categories(q, catalog))
    bus.register(ListZonesQuery, lambda q: handle_list_zones(q, catalog))

    return bus


def verify_internal_key(x_internal_key: str = Header(None)):
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal API key")

    return True


def _product_to_response(product) -> dict:
    return ProductResponse(
        id=product.id,
        sku=product.sku,
        barcode=product.barcode,
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        reserved=product.reserved,
        location=product.location,
        status=product.status.value if product.status else None,
        created_at=product.created_at,
    ).model_dump()


# =============================================================================
# INIT / SEED
# =============================================================================
def init_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        from .infrastructure.persistence.models import ProductModel
        if db.query(ProductModel).count() > 0:
            return
        print(f"[{SERVICE_NAME}] Initializing database...")

        categories = [
            CategoryModel(name="Электроника"),
            CategoryModel(name="Аудио"),
            CategoryModel(name="Компьютеры"),
        ]
        db.add_all(categories)

        products = [
            ProductModel(sku="PRD-001", barcode="4000000000001", name="iPhone 15 Pro", price=99990, stock=45, location="A-01-03", category_id=1, description="brand:Apple|country:США|category:Electronics|weight:221g|dimensions:15x7cm"),
            ProductModel(sku="PRD-002", barcode="4000000000002", name="Samsung Galaxy S24", price=84990, stock=32, location="A-01-04", category_id=1, description="brand:Samsung|country:Южная Корея|category:Electronics|weight:168g|dimensions:15x7cm"),
            ProductModel(sku="PRD-003", barcode="4000000000003", name="Sony WH-1000XM5", price=34990, stock=18, location="A-02-01", category_id=2, description="brand:Sony|country:Япония|category:Electronics|weight:250g|dimensions:20x18cm"),
            ProductModel(sku="PRD-004", barcode="4000000000004", name="MacBook Pro 14", price=199990, stock=12, location="A-03-01", category_id=3, description="brand:Apple|country:США|category:Computer Accessories|weight:1.6kg|dimensions:31x22cm"),
            ProductModel(sku="PRD-005", barcode="4000000000005", name="iPad Air", price=64990, stock=28, location="A-01-05", category_id=1, description="brand:Apple|country:Китай|category:Electronics|weight:461g|dimensions:25x17cm"),
            ProductModel(sku="PRD-006", barcode="4000000000006", name="AirPods Pro 2", price=24990, stock=56, location="A-02-02", category_id=2, description="brand:Apple|country:Вьетнам|category:Electronics|weight:50g|dimensions:5x5cm"),
            ProductModel(sku="PRD-007", barcode="4000000000007", name="Logitech MX Keys", price=8990, stock=8, location="B-01-01", category_id=3, description="brand:Logitech|country:Швейцария|category:Computer Accessories|weight:810g|dimensions:43x13cm"),
            ProductModel(sku="PRD-008", barcode="4000000000008", name="JBL Flip 6", price=12990, stock=24, location="B-01-02", category_id=2, description="brand:JBL|country:Китай|category:Electronics|weight:550g|dimensions:18x7cm"),
            ProductModel(sku="PRD-009", barcode="PRD12345", name="Беспроводные наушники", price=4990, stock=15, location="A-02-03", category_id=2, description="brand:Sony|country:Китай|category:Electronics|weight:250g|dimensions:10x5cm"),
            ProductModel(sku="PRD-010", barcode="PRD23456", name="Белковый порошок", price=3990, stock=40, location="C-01-01", category_id=1, description="brand:Optimum Nutrition|country:США|category:Health & Fitness|weight:2kg|dimensions:20x15cm"),
            ProductModel(sku="PRD-011", barcode="PRD34567", name="Механическая клавиатура", price=7990, stock=6, location="B-02-01", category_id=3, description="brand:Logitech|country:Тайвань|category:Computer Accessories|weight:1.2kg|dimensions:45x15cm"),
            ProductModel(sku="PRD-012", barcode="PRD45678", name="Кофеварка", price=15990, stock=3, location="C-02-01", category_id=1, description="brand:DeLonghi|country:Италия|category:Kitchen Appliances|weight:4kg|dimensions:30x25cm"),
        ]
        db.add_all(products)

        zones = [
            WarehouseZoneModel(code="A", name="Электроника", capacity=1000, used=750),
            WarehouseZoneModel(code="B", name="Бытовая техника", capacity=800, used=600),
            WarehouseZoneModel(code="C", name="Одежда", capacity=1200, used=400),
            WarehouseZoneModel(code="D", name="Продукты", capacity=500, used=480),
        ]
        db.add_all(zones)

        db.commit()
        print(f"[{SERVICE_NAME}] Database initialized!")
    finally:
        db.close()


# =============================================================================
# APP
# =============================================================================
@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    verify_redis_connection()
    print(f"[{SERVICE_NAME}] Starting on port {SERVICE_PORT} (DDD+CQRS+Redis)...")
    yield
    print(f"[{SERVICE_NAME}] Shutting down...")


app = FastAPI(
    title="Product Service (DDD + CQRS + Redis)",
    description="Микросервис управления товарами WMS.",
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
def health():
    return {"status": "ok", "service": SERVICE_NAME, "port": SERVICE_PORT, "architecture": "DDD+CQRS+Redis"}


@app.get("/products")
def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[int] = None,
    query_bus: QueryBus = Depends(get_query_bus),
):
    result = query_bus.ask(ListProductsQuery(page=page, limit=limit, search=search, category=category))

    return {
        "data": [_product_to_response(p) for p in result["items"]],
        "meta": {"page": result["page"], "limit": result["limit"], "total": result["total"]},
    }


@app.get("/products/{product_id}")
def get_product(product_id: int, query_bus: QueryBus = Depends(get_query_bus)):
    r = get_redis()
    cached = r.get(f"product:{product_id}")
    if cached is not None:
        return json.loads(cached)

    product = query_bus.ask(GetProductQuery(product_id=product_id))
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    response = _product_to_response(product)
    r.setex(f"product:{product_id}", 300, json.dumps(response, default=str))

    return response


@app.post("/products", status_code=201)
def create_product(
    data: ProductCreate,
    service: ProductApplicationService = Depends(get_product_service),
    command_bus: CommandBus = Depends(get_command_bus),
):
    existing = SQLAlchemyProductRepository(next(get_db())).find_by_sku(data.sku.strip())
    if existing is not None:
        raise HTTPException(status_code=409, detail="Такой артикул уже есть")

    try:
        product = command_bus.dispatch(
            CreateProductCommand(
                sku=data.sku,
                name=data.name,
                description=data.description,
                price=data.price,
                stock=data.stock,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    print(f"[{SERVICE_NAME}] Product {data.sku} created via CQRS+DDD")

    return _product_to_response(product)


@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    command_bus: CommandBus = Depends(get_command_bus),
):
    deleted = command_bus.dispatch(DeleteProductCommand(product_id=product_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")

    print(f"[{SERVICE_NAME}] Product {product_id} deleted")


@app.patch("/products/{product_id}")
def update_product(
    product_id: int,
    data: ProductUpdate,
    command_bus: CommandBus = Depends(get_command_bus),
):
    updates = data.model_dump(exclude_unset=True)
    product = command_bus.dispatch(
        UpdateProductCommand(product_id=product_id, **updates)
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    r = get_redis()
    r.delete(f"product:{product_id}")

    print(f"[{SERVICE_NAME}] Product {product_id} updated via CQRS: {list(updates.keys())}")
    return _product_to_response(product)


@app.get("/categories")
def get_categories(query_bus: QueryBus = Depends(get_query_bus)):
    return query_bus.ask(ListCategoriesQuery())


@app.get("/zones")
def get_zones(query_bus: QueryBus = Depends(get_query_bus)):
    return query_bus.ask(ListZonesQuery())


@app.post("/internal/reserve")
def reserve_products(
    data: ReserveRequest,
    _: bool = Depends(verify_internal_key),
    command_bus: CommandBus = Depends(get_command_bus),
):
    result = command_bus.dispatch(
        ReserveStockCommand(
            items=tuple({"product_id": i.product_id, "quantity": i.quantity} for i in data.items)
        )
    )

    print(f"[{SERVICE_NAME}] Reserved {len([i for i in result if i.get('reserved')])} items")

    return {"items": result}


@app.post("/internal/release")
def release_products(
    data: ReserveRequest,
    _: bool = Depends(verify_internal_key),
    command_bus: CommandBus = Depends(get_command_bus),
):
    result = command_bus.dispatch(
        ReleaseStockCommand(
            items=tuple({"product_id": i.product_id, "quantity": i.quantity} for i in data.items)
        )
    )

    print(f"[{SERVICE_NAME}] Released reserve for {len(data.items)} items")

    return result


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
