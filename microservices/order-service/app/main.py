"""
Order Service — CQRS + DDD architecture.

Layers:
  domain/         — Aggregate Root, Value Objects, Domain Events
  application/    — Commands, Queries, Handlers, CommandBus, QueryBus
  infrastructure/ — SQLAlchemy Repository, EventPublisher
  main.py         — FastAPI endpoints (thin adapter)
"""

from contextlib import asynccontextmanager
from typing import List, Optional
import json
import os

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .application.bus import CommandBus, QueryBus
from .application.commands import (
    CreateOrderCommand,
    ChangeStatusCommand,
    AddItemCommand,
    CancelOrderCommand,
)
from .application.commands.create_order_command import OrderItemData
from .application.queries import GetOrderQuery, ListOrdersQuery
from .application.handlers.command_handlers import (
    handle_create_order,
    handle_change_status,
    handle_add_item,
    handle_cancel_order,
)
from .application.handlers.query_handlers import handle_get_order, handle_list_orders
from .application.services import OrderApplicationService
from .application.services.order_application_service import CreateOrderDTO, AddItemDTO
from .infrastructure.persistence import Base, SQLAlchemyOrderRepository
from .infrastructure.redis_client import get_redis, verify_redis_connection
from .wms_config import require_env


# =============================================================================
# CONFIG
# =============================================================================
SERVICE_NAME = "order-service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8003"))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "orders.db")
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
class OrderItemCreateRequest(BaseModel):
    product_id: int
    product_name: str
    product_sku: str = ""
    quantity: int
    unit_price: float


class OrderCreateRequest(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    priority: str = "normal"
    notes: Optional[str] = None
    items: List[OrderItemCreateRequest] = []


class StatusUpdateRequest(BaseModel):
    status: str
    reason: Optional[str] = None


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_order_service(db: Session = Depends(get_db)) -> OrderApplicationService:
    repository = SQLAlchemyOrderRepository(db)
    return OrderApplicationService(order_repository=repository, event_publisher=None)


def get_command_bus(service: OrderApplicationService = Depends(get_order_service)) -> CommandBus:
    bus = CommandBus()
    bus.register(CreateOrderCommand, lambda cmd: handle_create_order(cmd, service))
    bus.register(ChangeStatusCommand, lambda cmd: handle_change_status(cmd, service))
    bus.register(AddItemCommand, lambda cmd: handle_add_item(cmd, service))
    bus.register(CancelOrderCommand, lambda cmd: handle_cancel_order(cmd, service))

    return bus


def get_query_bus(service: OrderApplicationService = Depends(get_order_service)) -> QueryBus:
    bus = QueryBus()
    bus.register(GetOrderQuery, lambda q: handle_get_order(q, service))
    bus.register(ListOrdersQuery, lambda q: handle_list_orders(q, service))

    return bus


def verify_internal_key(x_internal_key: str = Header(None)):
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal API key")

    return True


def _invalidate_order_cache(order_id: int | None = None) -> None:
    r = get_redis()
    if order_id is not None:
        r.delete(f"order:{order_id}")
    for key in r.scan_iter("orders:list:*"):
        r.delete(key)


# =============================================================================
# INIT / SEED
# =============================================================================
def init_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        repository = SQLAlchemyOrderRepository(db)
        if repository.count() > 0:
            return
        print(f"[{SERVICE_NAME}] Seeding initial data...")
        service = OrderApplicationService(repository)

        def make_order(customer_name, phone, address=None, priority="normal", items=(), statuses=()):
            order = service.create_order(CreateOrderDTO(
                customer_name=customer_name,
                customer_phone=phone,
                customer_address=address,
                priority=priority,
            ))
            for pid, name, sku, qty, price in items:
                order = service.add_item(order.id, AddItemDTO(
                    product_id=pid, product_name=name, product_sku=sku,
                    quantity=qty, unit_price=price,
                ))
            for s in statuses:
                order = service.change_status(order.id, s)

            return order

        make_order("Иван Иванов", "+7 999 123-45-67", "г. Москва, ул. Примерная, д. 1",
                   items=[(1, "iPhone 15 Pro", "IPH-15-PRO", 1, 134990.0)])
        make_order("Мария Петрова", "+7 999 234-56-78",
                   items=[(2, "MacBook Air M2", "MBA-M2", 1, 109990.0)],
                   statuses=["confirmed", "picking"])
        make_order("ООО Ромашка", "+7 495 111-22-33", priority="high",
                   items=[(3, "iMac 24", "IMAC-24", 2, 159990.0)],
                   statuses=["confirmed", "picking", "packed", "shipped"])
        make_order("Алексей Сидоров", "+7 916 555-12-34",
                   address="г. Санкт-Петербург, Невский пр., 10",
                   items=[(4, "MacBook Pro 14", "PRD-004", 1, 199990.0)],
                   statuses=["confirmed"])
        make_order("Елена Козлова", "+7 903 777-88-99",
                   items=[
                       (5, "iPad Air", "PRD-005", 2, 64990.0),
                       (6, "AirPods Pro 2", "PRD-006", 1, 24990.0),
                   ],
                   statuses=["confirmed", "picking"])
        make_order("ООО ТехноСнаб", "+7 495 900-11-22", priority="urgent",
                   items=[(7, "Logitech MX Keys", "PRD-007", 5, 8990.0)],
                   statuses=["confirmed", "picking"])
        make_order("Дмитрий Волков", "+7 926 111-22-33",
                   items=[(8, "JBL Flip 6", "PRD-008", 1, 12990.0)])
        make_order("Анна Смирнова", "+7 912 333-44-55", "г. Казань, ул. Баумана, 5",
                   items=[(3, "Sony WH-1000XM5", "PRD-003", 1, 34990.0)],
                   statuses=["confirmed", "picking", "packed"])

        print(f"[{SERVICE_NAME}] Database seeded!")
    finally:
        db.close()


# =============================================================================
# APP
# =============================================================================
@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    verify_redis_connection()
    print(f"[{SERVICE_NAME}] Starting on port {SERVICE_PORT} (CQRS + DDD + Redis)...")
    yield
    print(f"[{SERVICE_NAME}] Shutting down...")


app = FastAPI(
    title="Order Service (DDD + CQRS)",
    description="""
Микросервис управления заказами WMS.

## Архитектура DDD + CQRS

- **Domain Layer**: Order (Aggregate Root), OrderItem (Entity), Money & OrderStatus (Value Objects)
- **Application Layer**: CommandBus / QueryBus, Commands, Queries, Handlers, OrderApplicationService
- **Infrastructure Layer**: SQLAlchemyOrderRepository, EventPublisher

## State Machine

```
PENDING -> CONFIRMED -> PICKING -> PACKED -> SHIPPED -> DELIVERED
              |            |          |         |
              v            v          v         v
           CANCELLED  CANCELLED  CANCELLED  RETURNED
```
""",
    version="3.0.0",
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
# PUBLIC API ENDPOINTS
# =============================================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "port": SERVICE_PORT,
        "architecture": "DDD+CQRS+Redis",
    }


@app.get("/orders")
def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    query_bus: QueryBus = Depends(get_query_bus),
):
    cache_key = f"orders:list:{status or 'all'}:{page}:{limit}"
    r = get_redis()
    cached = r.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    result = query_bus.ask(ListOrdersQuery(status=status, page=page, limit=limit))
    r.setex(cache_key, 30, json.dumps(result, default=str))
    return result


@app.get("/orders/{order_id}")
def get_order(order_id: int, query_bus: QueryBus = Depends(get_query_bus)):
    cache_key = f"order:{order_id}"
    r = get_redis()
    cached = r.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    result = query_bus.ask(GetOrderQuery(order_id=order_id))
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")

    r.setex(cache_key, 30, json.dumps(result, default=str))
    return result


@app.post("/orders", status_code=201)
async def create_order(
    request: OrderCreateRequest,
    background_tasks: BackgroundTasks,
    command_bus: CommandBus = Depends(get_command_bus),
):
    command = CreateOrderCommand(
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
        customer_email=request.customer_email,
        customer_address=request.customer_address,
        priority=request.priority,
        notes=request.notes,
        items=[
            OrderItemData(
                product_id=i.product_id,
                product_name=i.product_name,
                product_sku=i.product_sku,
                quantity=i.quantity,
                unit_price=i.unit_price,
            )
            for i in request.items
        ],
    )
    try:
        order = command_bus.dispatch(command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    _invalidate_order_cache()

    background_tasks.add_task(
        notify_picking_service, order.id, order.order_number, order.priority
    )
    print(f"[{SERVICE_NAME}] Order {order.order_number} created via CQRS+DDD!")

    return order


@app.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    request: StatusUpdateRequest,
    command_bus: CommandBus = Depends(get_command_bus),
):
    try:
        result = command_bus.dispatch(
            ChangeStatusCommand(order_id=order_id, new_status=request.status, reason=request.reason)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    _invalidate_order_cache(order_id)
    return result


@app.post("/orders/{order_id}/items", status_code=201)
def add_item_to_order(
    order_id: int,
    request: OrderItemCreateRequest,
    command_bus: CommandBus = Depends(get_command_bus),
):
    try:
        result = command_bus.dispatch(
            AddItemCommand(
                order_id=order_id,
                product_id=request.product_id,
                product_name=request.product_name,
                product_sku=request.product_sku,
                quantity=request.quantity,
                unit_price=request.unit_price,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    _invalidate_order_cache(order_id)
    return result


@app.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    reason: Optional[str] = None,
    command_bus: CommandBus = Depends(get_command_bus),
):
    try:
        result = command_bus.dispatch(CancelOrderCommand(order_id=order_id, reason=reason))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    _invalidate_order_cache(order_id)
    return result


@app.post("/orders/{order_id}/confirm")
def confirm_order(
    order_id: int,
    command_bus: CommandBus = Depends(get_command_bus),
):
    try:
        result = command_bus.dispatch(ChangeStatusCommand(order_id=order_id, new_status="confirmed"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    _invalidate_order_cache(order_id)
    return result


@app.delete("/orders/{order_id}/items/{product_id}")
def remove_item_from_order(
    order_id: int,
    product_id: int,
    service: OrderApplicationService = Depends(get_order_service),
):
    try:
        result = service.remove_item(order_id, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    _invalidate_order_cache(order_id)
    return result


@app.delete("/orders/{order_id}", status_code=204)
def delete_order(
    order_id: int,
    service: OrderApplicationService = Depends(get_order_service),
):
    if not service.delete_order(order_id):
        raise HTTPException(status_code=404, detail="Order not found")

    _invalidate_order_cache(order_id)


# =============================================================================
# INTERNAL API
# =============================================================================

@app.patch("/internal/orders/{order_id}/status")
def update_order_status_internal(
    order_id: int,
    request: StatusUpdateRequest,
    _: bool = Depends(verify_internal_key),
    command_bus: CommandBus = Depends(get_command_bus),
):
    try:
        command_bus.dispatch(
            ChangeStatusCommand(order_id=order_id, new_status=request.status, reason=request.reason)
        )
        _invalidate_order_cache(order_id)
        return {"status": "updated", "order_id": order_id, "new_status": request.status}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/internal/orders/{order_id}")
def get_order_internal(
    order_id: int,
    _: bool = Depends(verify_internal_key),
    query_bus: QueryBus = Depends(get_query_bus),
):
    result = query_bus.ask(GetOrderQuery(order_id=order_id))
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")

    return result


# =============================================================================
# INTER-SERVICE COMMUNICATION
# =============================================================================
async def notify_picking_service(order_id: int, order_number: str, priority: str):
    import httpx

    picking_url = os.getenv("PICKING_SERVICE_URL", "http://localhost:8005")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{picking_url}/internal/tasks",
                json={"order_id": order_id, "order_number": order_number, "priority": priority},
                headers={"X-Internal-Key": INTERNAL_API_KEY},
            )
            if response.status_code == 201:
                print(f"[{SERVICE_NAME}] Picking task created for order {order_number}")
            else:
                print(f"[{SERVICE_NAME}] Picking notification failed: {response.status_code}")
    except Exception as exc:
        print(f"[{SERVICE_NAME}] Error notifying Picking: {exc}")


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
