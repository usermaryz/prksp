from contextlib import asynccontextmanager
from datetime import datetime
from functools import partial
from typing import Optional
import json
import os
import httpx

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .application.bus import CommandBus, QueryBus
from .application.commands import (
    CreateTaskCommand,
    StartTaskCommand,
    CompleteTaskCommand,
)
from .application.queries import GetTaskQuery, ListTasksQuery, GetStatsQuery
from .application.handlers import (
    handle_create_task,
    handle_start_task,
    handle_complete_task,
    handle_get_task,
    handle_list_tasks,
    handle_get_stats,
)
from .application.services import PickingApplicationService
from .infrastructure.persistence import Base, SQLAlchemyTaskRepository
from .infrastructure.redis_client import get_redis, verify_redis_connection
from .wms_config import require_env


# =============================================================================
# CONFIG
# =============================================================================
SERVICE_NAME = "picking-service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8005"))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "picking.db")


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

ORDER_SERVICE_URL = os.getenv(
    "ORDER_SERVICE_URL", "http://localhost:8003"
)
LOGISTICS_SERVICE_URL = os.getenv(
    "LOGISTICS_SERVICE_URL", "http://localhost:8006"
)

_connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================================================
# SCHEMAS
# =============================================================================
class TaskCreate(BaseModel):
    order_id: int
    order_number: str
    priority: str = "normal"
    items_count: int = 0


class TaskResponse(BaseModel):
    id: int
    order_id: int
    order_number: str
    status: str
    priority: str
    assigned_to: Optional[str]
    progress: int
    items_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# DEPENDENCIES
# =============================================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_service(
    db: Session = Depends(get_db),
) -> PickingApplicationService:
    repository = SQLAlchemyTaskRepository(db)

    return PickingApplicationService(repository)


def get_command_bus(
    service: PickingApplicationService = Depends(get_task_service),
) -> CommandBus:
    bus = CommandBus()
    bus.register(
        CreateTaskCommand,
        partial(handle_create_task, service=service),
    )
    bus.register(
        StartTaskCommand,
        partial(handle_start_task, service=service),
    )
    bus.register(
        CompleteTaskCommand,
        partial(handle_complete_task, service=service),
    )

    return bus


def get_query_bus(
    service: PickingApplicationService = Depends(get_task_service),
) -> QueryBus:
    bus = QueryBus()
    bus.register(
        GetTaskQuery,
        partial(handle_get_task, service=service),
    )
    bus.register(
        ListTasksQuery,
        partial(handle_list_tasks, service=service),
    )
    bus.register(
        GetStatsQuery,
        partial(handle_get_stats, service=service),
    )

    return bus


def verify_internal_key(x_internal_key: str = Header(None)):
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal API key")

    return True


# =============================================================================
# INTER-SERVICE COMMUNICATION
# =============================================================================
async def update_order_status(order_id: int, status: str, reason: str = None):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(
                f"{ORDER_SERVICE_URL}/internal/orders/{order_id}/status",
                json={"status": status, "reason": reason},
                headers={"X-Internal-Key": INTERNAL_API_KEY},
            )
            if response.status_code == 200:
                print(
                    f"[{SERVICE_NAME}] Order {order_id} "
                    f"status updated to {status}"
                )
            else:
                print(
                    f"[{SERVICE_NAME}] Failed to update order "
                    f"status: {response.status_code}"
                )
    except Exception as e:
        print(f"[{SERVICE_NAME}] Error updating order status: {e}")


async def get_order_details(order_id: int):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{ORDER_SERVICE_URL}/internal/orders/{order_id}",
                headers={"X-Internal-Key": INTERNAL_API_KEY},
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"[{SERVICE_NAME}] Error getting order details: {e}")

    return None


async def create_shipment(order_id: int, order_data: dict):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{LOGISTICS_SERVICE_URL}/internal/shipments",
                json={
                    "order_id": order_id,
                    "order_number": order_data.get("order_number"),
                    "recipient_name": order_data.get("customer_name"),
                    "recipient_phone": order_data.get("customer_phone"),
                    "delivery_address": order_data.get("customer_address"),
                },
                headers={"X-Internal-Key": INTERNAL_API_KEY},
            )
            if response.status_code == 201:
                print(
                    f"[{SERVICE_NAME}] Shipment created "
                    f"for order {order_id}"
                )

                return True
    except Exception as e:
        print(f"[{SERVICE_NAME}] Error creating shipment: {e}")

    return False


# =============================================================================
# INIT
# =============================================================================
def _fetch_orders_for_seed():
    import time

    for _ in range(8):
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(
                    f"{ORDER_SERVICE_URL}/orders",
                    params={"limit": 50},
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
        from .infrastructure.persistence.sqlalchemy_task_repository import SQLAlchemyTaskRepository

        task_repo = SQLAlchemyTaskRepository(db)
        if len(task_repo.find_all()) == 0:
            print(f"[{SERVICE_NAME}] Initializing database...")
            orders = _fetch_orders_for_seed()
            status_map = {
                "pending": ("pending", 0),
                "confirmed": ("pending", 0),
                "picking": ("in_progress", 55),
                "packed": ("completed", 100),
                "shipped": ("completed", 100),
                "delivered": ("completed", 100),
            }
            assignees = ["Иван П.", "Мария К.", "Алексей С.", "Сборщик А."]

            if orders:
                for index, order in enumerate(orders):
                    order_status = order.get("status", "pending")
                    task_status, progress = status_map.get(
                        order_status, ("pending", 0)
                    )
                    db.add(
                        PickingTaskModel(
                            order_id=order["id"],
                            order_number=order.get(
                                "order_number",
                                f"ORD-{order['id']}",
                            ),
                            status=task_status,
                            priority=order.get("priority", "normal"),
                            assigned_to=assignees[index % len(assignees)]
                            if task_status != "pending"
                            else None,
                            progress=progress,
                            items_count=max(1, order.get("items_count") or 1),
                        )
                    )
            else:
                db.add_all(
                    [
                        PickingTaskModel(
                            order_id=1,
                            order_number="ORD-DEMO-001",
                            status="pending",
                            items_count=2,
                        ),
                        PickingTaskModel(
                            order_id=2,
                            order_number="ORD-DEMO-002",
                            status="in_progress",
                            assigned_to="Иван П.",
                            progress=50,
                            items_count=3,
                        ),
                    ]
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
    print(f"[{SERVICE_NAME}] Starting on port {SERVICE_PORT}...")
    yield
    print(f"[{SERVICE_NAME}] Shutting down...")


app = FastAPI(
    title="Picking Service",
    description="Микросервис сборки заказов WMS",
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
# HELPERS
# =============================================================================
def _task_to_response(task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        order_id=task.order_id,
        order_number=task.order_number,
        status=task.status.value.value,
        priority=task.priority,
        assigned_to=task.assigned_to,
        progress=task.progress,
        items_count=task.items_count,
        created_at=task.created_at,
    )


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME, "port": SERVICE_PORT}


@app.get("/tasks")
def get_tasks(
    status: Optional[str] = None,
    query_bus: QueryBus = Depends(get_query_bus),
):
    tasks = query_bus.ask(ListTasksQuery(status=status))

    return [_task_to_response(t) for t in tasks]


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, query_bus: QueryBus = Depends(get_query_bus)):
    task = query_bus.ask(GetTaskQuery(task_id=task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return _task_to_response(task)


@app.post("/tasks/{task_id}/start", response_model=TaskResponse)
async def start_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    command_bus: CommandBus = Depends(get_command_bus),
):
    try:
        task = command_bus.dispatch(StartTaskCommand(task_id=task_id))
    except ValueError as exc:
        msg = str(exc)
        if "не найдена" in msg:
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=400, detail=msg)

    get_redis().delete("picking:stats")

    background_tasks.add_task(
        update_order_status,
        task.order_id,
        "picking",
        f"Сборка начата, исполнитель: {task.assigned_to}",
    )

    print(
        f"[{SERVICE_NAME}] Task {task_id} started "
        f"for order {task.order_number}"
    )

    return _task_to_response(task)


@app.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    command_bus: CommandBus = Depends(get_command_bus),
):
    try:
        task = command_bus.dispatch(CompleteTaskCommand(task_id=task_id))
    except ValueError as exc:
        msg = str(exc)
        if "не найдена" in msg:
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=400, detail=msg)

    get_redis().delete("picking:stats")

    background_tasks.add_task(
        update_order_status,
        task.order_id,
        "packed",
        "Сборка завершена",
    )

    async def create_shipment_flow():
        order_data = await get_order_details(task.order_id)
        if order_data:
            await create_shipment(task.order_id, order_data)
            await update_order_status(
                task.order_id, "shipped", "Отправление создано"
            )

    background_tasks.add_task(create_shipment_flow)

    print(
        f"[{SERVICE_NAME}] Task {task_id} completed "
        f"for order {task.order_number}"
    )

    return _task_to_response(task)


@app.get("/stats")
def get_stats(query_bus: QueryBus = Depends(get_query_bus)):
    r = get_redis()
    cached = r.get("picking:stats")
    if cached:
        return json.loads(cached)

    result = query_bus.ask(GetStatsQuery())
    r.setex("picking:stats", 30, json.dumps(result))

    return result


@app.post("/internal/tasks", response_model=TaskResponse, status_code=201)
def create_task_internal(
    data: TaskCreate,
    _: bool = Depends(verify_internal_key),
    command_bus: CommandBus = Depends(get_command_bus),
):
    task = command_bus.dispatch(
        CreateTaskCommand(
            order_id=data.order_id,
            order_number=data.order_number,
            priority=data.priority,
            items_count=data.items_count,
        )
    )

    print(f"[{SERVICE_NAME}] Task created for order {data.order_number}")

    return _task_to_response(task)


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
