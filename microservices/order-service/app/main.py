"""
Order Service - Микросервис заказов с DDD архитектурой
======================================================

Архитектура:
├── domain/           # Бизнес-логика (Entity, Value Objects, Events)
├── application/      # Use Cases (Application Services)
├── infrastructure/   # Реализация (Repository, Event Publisher)
└── main.py          # API Layer (FastAPI endpoints)

Порт: 8003
База данных: orders.db (SQLite)

Паттерны DDD:
- Aggregate Root (Order)
- Value Objects (Money, OrderStatus)
- Domain Events
- Repository Pattern
- Application Service
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
import os

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Domain Layer
from .domain.entities import Order
from .domain.value_objects import Money, OrderStatus, OrderStatusEnum

# Application Layer
from .application.services import OrderApplicationService
from .application.services.order_application_service import (
    CreateOrderDTO, 
    AddItemDTO,
    OrderDTO
)

# Infrastructure Layer
from .infrastructure.persistence import Base, SQLAlchemyOrderRepository
from .infrastructure.event_publisher import get_event_publisher


# =============================================================================
# CONFIG
# =============================================================================
SERVICE_NAME = "order-service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8003"))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "orders.db")
_raw_db = os.getenv("DATABASE_URL", "").strip()
DATABASE_URL = (
    _raw_db.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if _raw_db
    else f"sqlite:///{DATABASE_PATH}"
)
INTERNAL_API_KEY = "internal-service-key-2024"

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================================================
# PYDANTIC SCHEMAS (API Layer)
# =============================================================================
class OrderItemCreateRequest(BaseModel):
    """Запрос на добавление позиции"""
    product_id: int
    product_name: str
    product_sku: str = ""
    quantity: int
    unit_price: float


class OrderCreateRequest(BaseModel):
    """Запрос на создание заказа"""
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    priority: str = "normal"
    notes: Optional[str] = None
    items: List[OrderItemCreateRequest] = []


class StatusUpdateRequest(BaseModel):
    """Запрос на изменение статуса"""
    status: str
    reason: Optional[str] = None


# =============================================================================
# DEPENDENCIES (Dependency Injection)
# =============================================================================
def get_db():
    """Получение сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_order_service(db: Session = Depends(get_db)) -> OrderApplicationService:
    """
    Dependency Injection для Application Service.
    
    Собирает граф зависимостей:
    Session -> Repository -> ApplicationService
    """
    repository = SQLAlchemyOrderRepository(db)
    event_publisher = get_event_publisher()
    
    # Wrapper для асинхронной публикации
    async def publish_event(event):
        await event_publisher.publish(event)
    
    return OrderApplicationService(
        order_repository=repository,
        event_publisher=None  # События публикуем через BackgroundTasks
    )


def verify_internal_key(x_internal_key: str = Header(None)):
    """Проверка внутреннего API ключа"""
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal API key")
    return True


# =============================================================================
# INIT
# =============================================================================
def init_database():
    """Инициализация базы данных"""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        repository = SQLAlchemyOrderRepository(db)
        if repository.count() == 0:
            print(f"[{SERVICE_NAME}] Seeding initial data...")
            
            # Создаём тестовые заказы через Domain Layer
            service = OrderApplicationService(repository)
            
            # Заказ 1 - Pending
            order1 = service.create_order(CreateOrderDTO(
                customer_name="Иван Иванов",
                customer_phone="+7 999 123-45-67",
                customer_address="г. Москва, ул. Примерная, д. 1"
            ))
            service.add_item(order1.id, AddItemDTO(
                product_id=1,
                product_name="iPhone 15 Pro",
                product_sku="IPH-15-PRO",
                quantity=1,
                unit_price=134990.0
            ))
            
            # Заказ 2 - Picking
            order2 = service.create_order(CreateOrderDTO(
                customer_name="Мария Петрова",
                customer_phone="+7 999 234-56-78"
            ))
            service.add_item(order2.id, AddItemDTO(
                product_id=2,
                product_name="MacBook Air M2",
                product_sku="MBA-M2",
                quantity=1,
                unit_price=109990.0
            ))
            service.change_status(order2.id, "confirmed")
            service.change_status(order2.id, "picking")
            
            # Заказ 3 - Shipped
            order3 = service.create_order(CreateOrderDTO(
                customer_name="ООО Ромашка",
                customer_phone="+7 495 111-22-33",
                priority="high"
            ))
            service.add_item(order3.id, AddItemDTO(
                product_id=3,
                product_name="iMac 24",
                product_sku="IMAC-24",
                quantity=2,
                unit_price=159990.0
            ))
            service.change_status(order3.id, "confirmed")
            service.change_status(order3.id, "picking")
            service.change_status(order3.id, "packed")
            service.change_status(order3.id, "shipped")

            order4 = service.create_order(CreateOrderDTO(
                customer_name="Алексей Сидоров",
                customer_phone="+7 916 555-12-34",
                customer_address="г. Санкт-Петербург, Невский пр., 10",
            ))
            service.add_item(order4.id, AddItemDTO(
                product_id=4, product_name="MacBook Pro 14", product_sku="PRD-004",
                quantity=1, unit_price=199990.0,
            ))
            service.change_status(order4.id, "confirmed")

            order5 = service.create_order(CreateOrderDTO(
                customer_name="Елена Козлова",
                customer_phone="+7 903 777-88-99",
            ))
            service.add_item(order5.id, AddItemDTO(
                product_id=5, product_name="iPad Air", product_sku="PRD-005",
                quantity=2, unit_price=64990.0,
            ))
            service.add_item(order5.id, AddItemDTO(
                product_id=6, product_name="AirPods Pro 2", product_sku="PRD-006",
                quantity=1, unit_price=24990.0,
            ))
            service.change_status(order5.id, "confirmed")
            service.change_status(order5.id, "picking")

            order6 = service.create_order(CreateOrderDTO(
                customer_name="ООО ТехноСнаб",
                customer_phone="+7 495 900-11-22",
                priority="urgent",
            ))
            service.add_item(order6.id, AddItemDTO(
                product_id=7, product_name="Logitech MX Keys", product_sku="PRD-007",
                quantity=5, unit_price=8990.0,
            ))
            service.change_status(order6.id, "confirmed")
            service.change_status(order6.id, "picking")

            order7 = service.create_order(CreateOrderDTO(
                customer_name="Дмитрий Волков",
                customer_phone="+7 926 111-22-33",
            ))
            service.add_item(order7.id, AddItemDTO(
                product_id=8, product_name="JBL Flip 6", product_sku="PRD-008",
                quantity=1, unit_price=12990.0,
            ))

            order8 = service.create_order(CreateOrderDTO(
                customer_name="Анна Смирнова",
                customer_phone="+7 912 333-44-55",
                customer_address="г. Казань, ул. Баумана, 5",
            ))
            service.add_item(order8.id, AddItemDTO(
                product_id=3, product_name="Sony WH-1000XM5", product_sku="PRD-003",
                quantity=1, unit_price=34990.0,
            ))
            service.change_status(order8.id, "confirmed")
            service.change_status(order8.id, "picking")
            service.change_status(order8.id, "packed")
            
            print(f"[{SERVICE_NAME}] Database seeded!")
    finally:
        db.close()


# =============================================================================
# APP
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    print(f"[{SERVICE_NAME}] Starting on port {SERVICE_PORT}...")
    print(f"[{SERVICE_NAME}] DDD Architecture enabled!")
    yield
    print(f"[{SERVICE_NAME}] Shutting down...")


app = FastAPI(
    title="Order Service (DDD)",
    description="""
    Микросервис управления заказами WMS с Domain-Driven Design.
    
    ## Архитектура DDD
    
    - **Domain Layer**: Order (Aggregate Root), OrderItem (Entity), Money & OrderStatus (Value Objects)
    - **Application Layer**: OrderApplicationService (Use Cases)
    - **Infrastructure Layer**: SQLAlchemyOrderRepository, EventPublisher
    
    ## State Machine (переходы статусов)
    
    ```
    PENDING -> CONFIRMED -> PICKING -> PACKED -> SHIPPED -> DELIVERED
                  |            |          |         |
                  v            v          v         v
               CANCELLED  CANCELLED  CANCELLED  RETURNED
    ```
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
# PUBLIC API ENDPOINTS
# =============================================================================

@app.get("/health")
def health():
    """Health check"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "port": SERVICE_PORT,
        "architecture": "DDD"
    }


@app.get("/orders")
def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    service: OrderApplicationService = Depends(get_order_service)
):
    """
    Получить список заказов.
    
    Использует Application Service для выполнения Query.
    """
    return service.list_orders(status=status, page=page, limit=limit)


@app.get("/orders/{order_id}")
def get_order(
    order_id: int,
    service: OrderApplicationService = Depends(get_order_service)
):
    """Получить заказ по ID"""
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/orders", status_code=201)
async def create_order(
    request: OrderCreateRequest,
    background_tasks: BackgroundTasks,
    service: OrderApplicationService = Depends(get_order_service)
):
    """
    Создать новый заказ.
    
    Процесс (DDD):
    1. CreateOrderDTO передаётся в Application Service
    2. Application Service создаёт Order через фабричный метод
    3. Order генерирует Domain Event (OrderCreated)
    4. Repository сохраняет агрегат
    5. Events публикуются в Picking Service
    """
    # Создаём заказ через Application Service
    dto = CreateOrderDTO(
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
        customer_email=request.customer_email,
        customer_address=request.customer_address,
        priority=request.priority,
        notes=request.notes
    )
    
    order = service.create_order(dto)
    
    # Добавляем позиции
    for item in request.items:
        item_dto = AddItemDTO(
            product_id=item.product_id,
            product_name=item.product_name,
            product_sku=item.product_sku,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        order = service.add_item(order.id, item_dto)
    
    # Асинхронная публикация событий
    background_tasks.add_task(
        notify_picking_service,
        order.id,
        order.order_number,
        order.priority
    )
    
    print(f"[{SERVICE_NAME}] Order {order.order_number} created via DDD!")
    
    return order


@app.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    request: StatusUpdateRequest,
    service: OrderApplicationService = Depends(get_order_service)
):
    """
    Изменить статус заказа.
    
    Валидация переходов выполняется Value Object OrderStatus.
    При недопустимом переходе - ValueError -> HTTP 400.
    """
    try:
        order = service.change_status(order_id, request.status)
        print(f"[{SERVICE_NAME}] Order {order.order_number} status -> {request.status}")
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/orders/{order_id}/items", status_code=201)
def add_item_to_order(
    order_id: int,
    request: OrderItemCreateRequest,
    service: OrderApplicationService = Depends(get_order_service)
):
    """
    Добавить позицию в заказ.
    
    Бизнес-правило: можно добавлять только в статусах PENDING/CONFIRMED.
    Проверка выполняется в Domain Entity.
    """
    try:
        dto = AddItemDTO(
            product_id=request.product_id,
            product_name=request.product_name,
            product_sku=request.product_sku,
            quantity=request.quantity,
            unit_price=request.unit_price
        )
        return service.add_item(order_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/orders/{order_id}/items/{product_id}")
def remove_item_from_order(
    order_id: int,
    product_id: int,
    service: OrderApplicationService = Depends(get_order_service)
):
    """Удалить позицию из заказа"""
    try:
        return service.remove_item(order_id, product_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/orders/{order_id}/confirm")
def confirm_order(
    order_id: int,
    service: OrderApplicationService = Depends(get_order_service)
):
    """Подтвердить заказ (PENDING -> CONFIRMED)"""
    try:
        return service.confirm_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    reason: Optional[str] = None,
    service: OrderApplicationService = Depends(get_order_service)
):
    """Отменить заказ"""
    try:
        return service.cancel_order(order_id, reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/orders/{order_id}", status_code=204)
def delete_order(
    order_id: int,
    service: OrderApplicationService = Depends(get_order_service)
):
    """Удалить заказ"""
    if not service.delete_order(order_id):
        raise HTTPException(status_code=404, detail="Order not found")


# =============================================================================
# INTERNAL API (для других микросервисов)
# =============================================================================

@app.patch("/internal/orders/{order_id}/status")
def update_order_status_internal(
    order_id: int,
    request: StatusUpdateRequest,
    _: bool = Depends(verify_internal_key),
    service: OrderApplicationService = Depends(get_order_service)
):
    """
    Обновление статуса (Internal API).
    
    Используется Picking Service и Logistics Service.
    """
    try:
        order = service.change_status(order_id, request.status)
        return {"status": "updated", "order_id": order_id, "new_status": request.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/internal/orders/{order_id}")
def get_order_internal(
    order_id: int,
    _: bool = Depends(verify_internal_key),
    service: OrderApplicationService = Depends(get_order_service)
):
    """Получить заказ (Internal API)"""
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# =============================================================================
# INTER-SERVICE COMMUNICATION
# =============================================================================
async def notify_picking_service(order_id: int, order_number: str, priority: str):
    """Уведомление Picking Service о новом заказе"""
    import httpx
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "http://localhost:8004/internal/tasks",
                json={
                    "order_id": order_id,
                    "order_number": order_number,
                    "priority": priority
                },
                headers={"X-Internal-Key": INTERNAL_API_KEY}
            )
            if response.status_code == 201:
                print(f"[{SERVICE_NAME}] Task created in Picking Service")
            else:
                print(f"[{SERVICE_NAME}] Picking notification failed: {response.status_code}")
    except Exception as e:
        print(f"[{SERVICE_NAME}] Error notifying Picking: {e}")


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
