"""
Logistics Service — CQRS + DDD architecture.

Layers:
  domain/         — Shipment (Aggregate Root), Carrier, ShipmentStatus (Value Object), Domain Events
  application/    — Commands, Queries, Handlers, CommandBus, QueryBus, LogisticsApplicationService
  infrastructure/ — SQLAlchemy Repositories, Redis client
  main.py         — FastAPI endpoints (thin adapter)
"""

import json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional
import os
import httpx

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .application.bus import CommandBus, QueryBus
from .application.commands import (
    CreateShipmentCommand,
    CreateShipmentInternalCommand,
)
from .application.queries import (
    GetShipmentQuery,
    ListShipmentsQuery,
    ListCarriersQuery,
    GetStatsQuery,
)
from .application.handlers.command_handlers import (
    handle_create_shipment,
    handle_create_shipment_internal,
)
from .application.handlers.query_handlers import (
    handle_get_shipment,
    handle_list_shipments,
    handle_list_carriers,
    handle_get_stats,
)
from .application.services import LogisticsApplicationService
from .infrastructure.persistence import (
    Base,
    SQLAlchemyShipmentRepository,
    SQLAlchemyCarrierRepository,
    ShipmentModel,
    CarrierModel,
)
from .infrastructure.redis_client import get_redis, verify_redis_connection
from .wms_config import require_env


# =============================================================================
# CONFIG
# =============================================================================
SERVICE_NAME = "logistics-service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8006"))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "logistics.db")


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
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8003")

_connect_args = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================
class ShipmentCreate(BaseModel):
    order_id: int
    carrier_id: int = 1
    delivery_method: str = "courier"


class ShipmentCreateInternal(BaseModel):
    order_id: int
    order_number: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    delivery_address: Optional[str] = None


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_logistics_service(
    db: Session = Depends(get_db),
) -> LogisticsApplicationService:
    shipment_repo = SQLAlchemyShipmentRepository(db)
    carrier_repo = SQLAlchemyCarrierRepository(db)

    return LogisticsApplicationService(
        shipment_repo=shipment_repo,
        carrier_repo=carrier_repo,
    )


def get_command_bus(
    service: LogisticsApplicationService = Depends(get_logistics_service),
) -> CommandBus:
    bus = CommandBus()
    bus.register(
        CreateShipmentCommand,
        lambda cmd: handle_create_shipment(cmd, service),
    )
    bus.register(
        CreateShipmentInternalCommand,
        lambda cmd: handle_create_shipment_internal(cmd, service),
    )

    return bus


def get_query_bus(
    service: LogisticsApplicationService = Depends(get_logistics_service),
) -> QueryBus:
    bus = QueryBus()
    bus.register(GetShipmentQuery, lambda q: handle_get_shipment(q, service))
    bus.register(
        ListShipmentsQuery, lambda q: handle_list_shipments(q, service)
    )
    bus.register(
        ListCarriersQuery, lambda q: handle_list_carriers(q, service)
    )
    bus.register(GetStatsQuery, lambda q: handle_get_stats(q, service))

    return bus


def verify_internal_key(x_internal_key: str = Header(None)):
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal API key")

    return True


# =============================================================================
# INTER-SERVICE COMMUNICATION
# =============================================================================
async def update_order_status(
    order_id: int, status: str, reason: str = None
):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.patch(
                f"{ORDER_SERVICE_URL}/internal/orders/{order_id}/status",
                json={"status": status, "reason": reason},
                headers={"X-Internal-Key": INTERNAL_API_KEY},
            )
            print(
                f"[{SERVICE_NAME}] Order {order_id} status updated to {status}"
            )
    except Exception as e:
        print(f"[{SERVICE_NAME}] Error updating order status: {e}")


# =============================================================================
# INIT
# =============================================================================
def _fetch_orders_for_seed():
    import time

    for _ in range(8):
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(
                    f"{ORDER_SERVICE_URL}/orders", params={"limit": 50}
                )
                if response.status_code == 200:
                    return response.json().get("data", [])
        except Exception as exc:
            print(f"[{SERVICE_NAME}] Waiting for order-service: {exc}")
        time.sleep(0.6)

    return []


def init_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        from .infrastructure.persistence.sqlalchemy_carrier_repository import (
            SQLAlchemyCarrierRepository,
        )

        if len(SQLAlchemyCarrierRepository(db).find_all_active()) == 0:
            print(f"[{SERVICE_NAME}] Initializing database...")

            carriers = [
                CarrierModel(code="cdek", name="СДЭК"),
                CarrierModel(code="boxberry", name="Boxberry"),
                CarrierModel(code="russian_post", name="Почта России"),
                CarrierModel(code="dpd", name="DPD"),
            ]
            db.add_all(carriers)
            db.flush()

            orders = _fetch_orders_for_seed()
            carrier_names = ["СДЭК", "Boxberry", "Почта России", "DPD"]
            tracking_idx = 1

            for order in orders:
                status = order.get("status", "")
                if status not in ("packed", "shipped", "delivered"):
                    continue
                shipment_status = (
                    "delivered" if status == "delivered"
                    else ("in_transit" if status == "shipped" else "pending")
                )
                db.add(
                    ShipmentModel(
                        order_id=order["id"],
                        order_number=order.get("order_number"),
                        tracking_number=(
                            f"WMS"
                            f"{datetime.utcnow().strftime('%y%m%d')}"
                            f"{tracking_idx:04d}"
                        ),
                        carrier_id=(tracking_idx % 4) + 1,
                        carrier_name=carrier_names[
                            tracking_idx % len(carrier_names)
                        ],
                        status=shipment_status,
                        recipient_name=order.get("customer_name"),
                        recipient_phone=order.get("customer_phone"),
                        delivery_address=order.get("customer_address"),
                        estimated_delivery=(
                            datetime.utcnow() + timedelta(days=3)
                        ).strftime("%d.%m.%Y"),
                    )
                )
                tracking_idx += 1

            if tracking_idx == 1:
                db.add(
                    ShipmentModel(
                        order_id=3,
                        order_number="ORD-DEMO-003",
                        tracking_number="WMS240601001",
                        carrier_name="СДЭК",
                        status="in_transit",
                        recipient_name="ООО Ромашка",
                        estimated_delivery="08.12.2026",
                    )
                )

            db.commit()
            print(f"[{SERVICE_NAME}] Database initialized!")
    finally:
        db.close()


# =============================================================================
# APP
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    verify_redis_connection()
    print(f"[{SERVICE_NAME}] Starting on port {SERVICE_PORT} (CQRS + DDD + Redis)...")
    yield
    print(f"[{SERVICE_NAME}] Shutting down...")


app = FastAPI(
    title="Logistics Service (DDD + CQRS)",
    description="Микросервис логистики WMS",
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
    return {"status": "ok", "service": SERVICE_NAME, "port": SERVICE_PORT}


@app.get("/shipments")
def get_shipments(
    status: Optional[str] = None,
    query_bus: QueryBus = Depends(get_query_bus),
):
    return query_bus.ask(ListShipmentsQuery(status=status))


@app.get("/shipments/{shipment_id}")
def get_shipment(
    shipment_id: int, query_bus: QueryBus = Depends(get_query_bus)
):
    result = query_bus.ask(GetShipmentQuery(shipment_id=shipment_id))
    if not result:
        raise HTTPException(status_code=404, detail="Shipment not found")

    return result


@app.post("/shipments", status_code=201)
async def create_shipment(
    data: ShipmentCreate,
    background_tasks: BackgroundTasks,
    command_bus: CommandBus = Depends(get_command_bus),
):
    result = command_bus.dispatch(
        CreateShipmentCommand(
            order_id=data.order_id,
            carrier_id=data.carrier_id,
            delivery_method=data.delivery_method,
        )
    )

    get_redis().delete("logistics:stats")

    background_tasks.add_task(
        update_order_status,
        data.order_id,
        "shipped",
        f"Отправление создано, трек: {result.tracking_number}",
    )
    print(
        f"[{SERVICE_NAME}] Shipment {result.tracking_number} "
        f"created for order {data.order_id}"
    )

    return result


@app.get("/carriers")
def get_carriers(query_bus: QueryBus = Depends(get_query_bus)):
    r = get_redis()
    cached = r.get("logistics:carriers")
    if cached:
        return json.loads(cached)

    result = query_bus.ask(ListCarriersQuery())
    r.setex("logistics:carriers", 600, json.dumps(result))

    return result


@app.get("/stats")
def get_stats(query_bus: QueryBus = Depends(get_query_bus)):
    r = get_redis()
    cached = r.get("logistics:stats")
    if cached:
        return json.loads(cached)

    result = query_bus.ask(GetStatsQuery())
    r.setex("logistics:stats", 30, json.dumps(result))

    return result


@app.post("/internal/shipments", status_code=201)
def create_shipment_internal(
    data: ShipmentCreateInternal,
    _: bool = Depends(verify_internal_key),
    command_bus: CommandBus = Depends(get_command_bus),
):
    result = command_bus.dispatch(
        CreateShipmentInternalCommand(
            order_id=data.order_id,
            order_number=data.order_number,
            recipient_name=data.recipient_name,
            recipient_phone=data.recipient_phone,
            delivery_address=data.delivery_address,
        )
    )

    get_redis().delete("logistics:stats")

    return result


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
