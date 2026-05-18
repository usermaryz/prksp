"""
Picking Service - Микросервис сборки заказов
============================================
База данных: picking.db
Порт: 8004

Ответственность:
- Управление задачами сборки
- Получение событий от Order Service
- Отправка обновлений в Order Service
- Создание отправлений в Logistics Service
"""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
import os
import httpx

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base


# =============================================================================
# CONFIG
# =============================================================================
SERVICE_NAME = "picking-service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8005"))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "picking.db")
_raw_db = os.getenv("DATABASE_URL", "").strip()
DATABASE_URL = (
    _raw_db.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if _raw_db
    else f"sqlite:///{DATABASE_PATH}"
)
INTERNAL_API_KEY = "internal-service-key-2024"

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8003")
LOGISTICS_SERVICE_URL = os.getenv("LOGISTICS_SERVICE_URL", "http://localhost:8006")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# =============================================================================
# MODELS
# =============================================================================
class PickingTask(Base):
    __tablename__ = "picking_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    order_number = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")
    priority = Column(String(10), default="normal")
    assigned_to = Column(String(100))
    progress = Column(Integer, default=0)
    items_count = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


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


def verify_internal_key(x_internal_key: str = Header(None)):
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal API key")
    return True


# =============================================================================
# INTER-SERVICE COMMUNICATION
# =============================================================================
async def update_order_status(order_id: int, status: str, reason: str = None):
    """
    Обновление статуса заказа в Order Service.
    Межсервисное взаимодействие.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(
                f"{ORDER_SERVICE_URL}/internal/orders/{order_id}/status",
                json={"status": status, "reason": reason},
                headers={"X-Internal-Key": INTERNAL_API_KEY}
            )
            if response.status_code == 200:
                print(f"[{SERVICE_NAME}] Order {order_id} status updated to {status}")
            else:
                print(f"[{SERVICE_NAME}] Failed to update order status: {response.status_code}")
    except Exception as e:
        print(f"[{SERVICE_NAME}] Error updating order status: {e}")


async def get_order_details(order_id: int):
    """Получение данных заказа из Order Service"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{ORDER_SERVICE_URL}/internal/orders/{order_id}",
                headers={"X-Internal-Key": INTERNAL_API_KEY}
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"[{SERVICE_NAME}] Error getting order details: {e}")
    return None


async def create_shipment(order_id: int, order_data: dict):
    """
    Создание отправления в Logistics Service.
    Вызывается после завершения сборки.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{LOGISTICS_SERVICE_URL}/internal/shipments",
                json={
                    "order_id": order_id,
                    "order_number": order_data.get("order_number"),
                    "recipient_name": order_data.get("customer_name"),
                    "recipient_phone": order_data.get("customer_phone"),
                    "delivery_address": order_data.get("customer_address")
                },
                headers={"X-Internal-Key": INTERNAL_API_KEY}
            )
            if response.status_code == 201:
                print(f"[{SERVICE_NAME}] Shipment created for order {order_id}")
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
                response = client.get(f"{ORDER_SERVICE_URL}/orders", params={"limit": 50})
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
        if db.query(PickingTask).count() == 0:
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
                    task_status, progress = status_map.get(order_status, ("pending", 0))
                    db.add(
                        PickingTask(
                            order_id=order["id"],
                            order_number=order.get("order_number", f"ORD-{order['id']}"),
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
                        PickingTask(
                            order_id=1,
                            order_number="ORD-DEMO-001",
                            status="pending",
                            items_count=2,
                        ),
                        PickingTask(
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
    print(f"[{SERVICE_NAME}] Starting on port {SERVICE_PORT}...")
    yield
    print(f"[{SERVICE_NAME}] Shutting down...")


app = FastAPI(
    title="Picking Service",
    description="Микросервис сборки заказов WMS",
    version="1.0.0",
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


# ==================== Public API ====================

@app.get("/tasks")
def get_tasks(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Получить список задач сборки"""
    query = db.query(PickingTask)
    if status:
        query = query.filter(PickingTask.status == status)
    
    tasks = query.order_by(PickingTask.created_at.desc()).all()
    return [TaskResponse.model_validate(t) for t in tasks]


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Получить задачу по ID"""
    task = db.query(PickingTask).filter(PickingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@app.post("/tasks/{task_id}/start", response_model=TaskResponse)
async def start_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Взять задачу в работу.
    Обновляет статус заказа в Order Service.
    """
    task = db.query(PickingTask).filter(PickingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "pending":
        raise HTTPException(status_code=400, detail="Task is not pending")
    
    task.status = "in_progress"
    task.started_at = datetime.utcnow()
    task.assigned_to = "Текущий пользователь"
    db.commit()
    db.refresh(task)
    
    # Асинхронно обновляем статус заказа
    background_tasks.add_task(
        update_order_status,
        task.order_id,
        "picking",
        f"Сборка начата, исполнитель: {task.assigned_to}"
    )
    
    print(f"[{SERVICE_NAME}] Task {task_id} started for order {task.order_number}")
    
    return TaskResponse.model_validate(task)


@app.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Завершить задачу сборки.
    1. Обновляет статус заказа в Order Service
    2. Создаёт отправление в Logistics Service
    """
    task = db.query(PickingTask).filter(PickingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "in_progress":
        raise HTTPException(status_code=400, detail="Task is not in progress")
    
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    task.progress = 100
    db.commit()
    db.refresh(task)
    
    # Асинхронно:
    # 1. Обновляем статус заказа на "packed"
    background_tasks.add_task(
        update_order_status,
        task.order_id,
        "packed",
        "Сборка завершена"
    )
    
    # 2. Получаем данные заказа и создаём отправление
    async def create_shipment_flow():
        order_data = await get_order_details(task.order_id)
        if order_data:
            await create_shipment(task.order_id, order_data)
            await update_order_status(task.order_id, "shipped", "Отправление создано")
    
    background_tasks.add_task(create_shipment_flow)
    
    print(f"[{SERVICE_NAME}] Task {task_id} completed for order {task.order_number}")
    
    return TaskResponse.model_validate(task)


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Статистика сборки"""
    pending = db.query(PickingTask).filter(PickingTask.status == "pending").count()
    in_progress = db.query(PickingTask).filter(PickingTask.status == "in_progress").count()
    completed = db.query(PickingTask).filter(PickingTask.status == "completed").count()
    
    return {
        "pending": pending,
        "in_progress": in_progress,
        "completed_today": completed,
        "average_time_minutes": 12
    }


# ==================== Internal API (для Order Service) ====================

@app.post("/internal/tasks", response_model=TaskResponse, status_code=201)
def create_task_internal(
    data: TaskCreate,
    _: bool = Depends(verify_internal_key),
    db: Session = Depends(get_db)
):
    """
    Создание задачи сборки (внутренний API).
    Вызывается Order Service при создании заказа.
    """
    # Проверяем, нет ли уже задачи для этого заказа
    existing = db.query(PickingTask).filter(PickingTask.order_id == data.order_id).first()
    if existing:
        return TaskResponse.model_validate(existing)
    
    task = PickingTask(
        order_id=data.order_id,
        order_number=data.order_number,
        priority=data.priority,
        items_count=data.items_count
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    print(f"[{SERVICE_NAME}] Task created for order {data.order_number}")
    
    return TaskResponse.model_validate(task)


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
