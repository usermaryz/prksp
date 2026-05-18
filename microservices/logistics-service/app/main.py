"""
Logistics Service - Микросервис логистики
=========================================
База данных: logistics.db
Порт: 8005

Ответственность:
- Управление отправлениями
- Отслеживание доставки
- Интеграция с перевозчиками
"""
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional
import os
import random
import httpx

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, Session, declarative_base


# =============================================================================
# CONFIG
# =============================================================================
SERVICE_NAME = "logistics-service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8006"))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "logistics.db")
_raw_db = os.getenv("DATABASE_URL", "").strip()
DATABASE_URL = (
    _raw_db.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if _raw_db
    else f"sqlite:///{DATABASE_PATH}"
)
INTERNAL_API_KEY = "internal-service-key-2024"

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8003")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# =============================================================================
# MODELS
# =============================================================================
class Shipment(Base):
    __tablename__ = "shipments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    order_number = Column(String(50))
    tracking_number = Column(String(100), unique=True, nullable=False, index=True)
    carrier_id = Column(Integer)
    carrier_name = Column(String(100))
    delivery_method = Column(String(20), default="courier")
    status = Column(String(30), default="pending")
    recipient_name = Column(String(100))
    recipient_phone = Column(String(20))
    delivery_address = Column(Text)
    estimated_delivery = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)


class Carrier(Base):
    __tablename__ = "carriers"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Integer, default=1)


# =============================================================================
# SCHEMAS
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


class ShipmentResponse(BaseModel):
    id: int
    order_id: int
    order_number: Optional[str]
    tracking_number: str
    carrier_name: Optional[str]
    status: str
    recipient_name: Optional[str]
    delivery_address: Optional[str]
    estimated_delivery: Optional[str]
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
    """Обновление статуса заказа в Order Service"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.patch(
                f"{ORDER_SERVICE_URL}/internal/orders/{order_id}/status",
                json={"status": status, "reason": reason},
                headers={"X-Internal-Key": INTERNAL_API_KEY}
            )
            print(f"[{SERVICE_NAME}] Order {order_id} status updated to {status}")
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
        if db.query(Carrier).count() == 0:
            print(f"[{SERVICE_NAME}] Initializing database...")

            carriers = [
                Carrier(code="cdek", name="СДЭК"),
                Carrier(code="boxberry", name="Boxberry"),
                Carrier(code="russian_post", name="Почта России"),
                Carrier(code="dpd", name="DPD"),
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
                shipment_status = "delivered" if status == "delivered" else (
                    "in_transit" if status == "shipped" else "pending"
                )
                db.add(
                    Shipment(
                        order_id=order["id"],
                        order_number=order.get("order_number"),
                        tracking_number=f"WMS{datetime.utcnow().strftime('%y%m%d')}{tracking_idx:04d}",
                        carrier_id=(tracking_idx % 4) + 1,
                        carrier_name=carrier_names[tracking_idx % len(carrier_names)],
                        status=shipment_status,
                        recipient_name=order.get("customer_name"),
                        recipient_phone=order.get("customer_phone"),
                        delivery_address=order.get("customer_address"),
                        estimated_delivery=(datetime.utcnow() + timedelta(days=3)).strftime("%d.%m.%Y"),
                    )
                )
                tracking_idx += 1

            if tracking_idx == 1:
                db.add(
                    Shipment(
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
    print(f"[{SERVICE_NAME}] Starting on port {SERVICE_PORT}...")
    yield
    print(f"[{SERVICE_NAME}] Shutting down...")


app = FastAPI(
    title="Logistics Service",
    description="Микросервис логистики WMS",
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

@app.get("/shipments")
def get_shipments(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Список отправлений"""
    query = db.query(Shipment)
    if status:
        query = query.filter(Shipment.status == status)
    
    shipments = query.order_by(Shipment.created_at.desc()).all()
    return [ShipmentResponse.model_validate(s) for s in shipments]


@app.get("/shipments/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    """Получить отправление"""
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return ShipmentResponse.model_validate(shipment)


@app.post("/shipments", response_model=ShipmentResponse, status_code=201)
async def create_shipment(
    data: ShipmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Создать отправление"""
    carrier = db.query(Carrier).filter(Carrier.id == data.carrier_id).first()
    
    tracking = f"WMS{datetime.now().strftime('%y%m%d')}{random.randint(10000, 99999)}"
    
    shipment = Shipment(
        order_id=data.order_id,
        tracking_number=tracking,
        carrier_id=data.carrier_id,
        carrier_name=carrier.name if carrier else None,
        delivery_method=data.delivery_method,
        estimated_delivery=(datetime.now() + timedelta(days=3)).strftime("%d.%m.%Y")
    )
    
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    
    # Обновляем статус заказа
    background_tasks.add_task(
        update_order_status,
        data.order_id,
        "shipped",
        f"Отправление создано, трек: {tracking}"
    )
    
    print(f"[{SERVICE_NAME}] Shipment {tracking} created for order {data.order_id}")
    
    return ShipmentResponse.model_validate(shipment)


@app.get("/carriers")
def get_carriers(db: Session = Depends(get_db)):
    """Список перевозчиков"""
    carriers = db.query(Carrier).filter(Carrier.is_active == 1).all()
    return [{"id": c.id, "code": c.code, "name": c.name} for c in carriers]


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Статистика логистики"""
    total = db.query(Shipment).count()
    pending = db.query(Shipment).filter(Shipment.status == "pending").count()
    in_transit = db.query(Shipment).filter(Shipment.status == "in_transit").count()
    delivered = db.query(Shipment).filter(Shipment.status == "delivered").count()
    
    return {
        "total": total,
        "pending": pending,
        "in_transit": in_transit,
        "delivered": delivered
    }


# ==================== Internal API (для Picking Service) ====================

@app.post("/internal/shipments", response_model=ShipmentResponse, status_code=201)
def create_shipment_internal(
    data: ShipmentCreateInternal,
    _: bool = Depends(verify_internal_key),
    db: Session = Depends(get_db)
):
    """
    Создание отправления (внутренний API).
    Вызывается Picking Service после завершения сборки.
    """
    # Проверяем, нет ли уже отправления для этого заказа
    existing = db.query(Shipment).filter(Shipment.order_id == data.order_id).first()
    if existing:
        return ShipmentResponse.model_validate(existing)
    
    # Выбираем первого доступного перевозчика
    carrier = db.query(Carrier).filter(Carrier.is_active == 1).first()
    
    tracking = f"WMS{datetime.now().strftime('%y%m%d')}{random.randint(10000, 99999)}"
    
    shipment = Shipment(
        order_id=data.order_id,
        order_number=data.order_number,
        tracking_number=tracking,
        carrier_id=carrier.id if carrier else None,
        carrier_name=carrier.name if carrier else "СДЭК",
        recipient_name=data.recipient_name,
        recipient_phone=data.recipient_phone,
        delivery_address=data.delivery_address,
        estimated_delivery=(datetime.now() + timedelta(days=3)).strftime("%d.%m.%Y")
    )
    
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    
    print(f"[{SERVICE_NAME}] Internal: Shipment {tracking} created for order {data.order_id}")
    
    return ShipmentResponse.model_validate(shipment)


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
