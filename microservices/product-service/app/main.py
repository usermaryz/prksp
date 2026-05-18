"""
Product Service - Микросервис товаров
=====================================
База данных: products.db
Порт: 8002

Ответственность:
- Каталог товаров
- Управление остатками
- Резервирование товаров для заказов
"""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
import os
import random

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Text, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base


# =============================================================================
# CONFIG
# =============================================================================
SERVICE_NAME = "product-service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8002"))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "products.db")
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
Base = declarative_base()


# =============================================================================
# MODELS
# =============================================================================
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    barcode = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(12, 2))
    category_id = Column(Integer)
    status = Column(String(20), default="active")
    stock = Column(Integer, default=0)
    reserved = Column(Integer, default=0)
    location = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)


class WarehouseZone(Base):
    __tablename__ = "warehouse_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, default=1000)
    used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


# =============================================================================
# SCHEMAS
# =============================================================================
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: int = 0


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
    created_at: datetime

    class Config:
        from_attributes = True


class ReserveItem(BaseModel):
    product_id: int
    quantity: int


class ReserveRequest(BaseModel):
    items: List[ReserveItem]


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
# INIT
# =============================================================================
def init_database():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            print(f"[{SERVICE_NAME}] Initializing database...")
            
            categories = [
                Category(name="Электроника"),
                Category(name="Аудио"),
                Category(name="Компьютеры"),
            ]
            db.add_all(categories)
            
            products = [
                Product(sku="PRD-001", barcode="4000000000001", name="iPhone 15 Pro", price=99990, stock=45, location="A-01-03", category_id=1, description="brand:Apple|country:США|category:Electronics|weight:221g|dimensions:15x7cm"),
                Product(sku="PRD-002", barcode="4000000000002", name="Samsung Galaxy S24", price=84990, stock=32, location="A-01-04", category_id=1, description="brand:Samsung|country:Южная Корея|category:Electronics|weight:168g|dimensions:15x7cm"),
                Product(sku="PRD-003", barcode="4000000000003", name="Sony WH-1000XM5", price=34990, stock=18, location="A-02-01", category_id=2, description="brand:Sony|country:Япония|category:Electronics|weight:250g|dimensions:20x18cm"),
                Product(sku="PRD-004", barcode="4000000000004", name="MacBook Pro 14", price=199990, stock=12, location="A-03-01", category_id=3, description="brand:Apple|country:США|category:Computer Accessories|weight:1.6kg|dimensions:31x22cm"),
                Product(sku="PRD-005", barcode="4000000000005", name="iPad Air", price=64990, stock=28, location="A-01-05", category_id=1, description="brand:Apple|country:Китай|category:Electronics|weight:461g|dimensions:25x17cm"),
                Product(sku="PRD-006", barcode="4000000000006", name="AirPods Pro 2", price=24990, stock=56, location="A-02-02", category_id=2, description="brand:Apple|country:Вьетнам|category:Electronics|weight:50g|dimensions:5x5cm"),
                Product(sku="PRD-007", barcode="4000000000007", name="Logitech MX Keys", price=8990, stock=8, location="B-01-01", category_id=3, description="brand:Logitech|country:Швейцария|category:Computer Accessories|weight:810g|dimensions:43x13cm"),
                Product(sku="PRD-008", barcode="4000000000008", name="JBL Flip 6", price=12990, stock=24, location="B-01-02", category_id=2, description="brand:JBL|country:Китай|category:Electronics|weight:550g|dimensions:18x7cm"),
                Product(sku="PRD-009", barcode="PRD12345", name="Беспроводные наушники", price=4990, stock=15, location="A-02-03", category_id=2, description="brand:Sony|country:Китай|category:Electronics|weight:250g|dimensions:10x5cm"),
                Product(sku="PRD-010", barcode="PRD23456", name="Белковый порошок", price=3990, stock=40, location="C-01-01", category_id=1, description="brand:Optimum Nutrition|country:США|category:Health & Fitness|weight:2kg|dimensions:20x15cm"),
                Product(sku="PRD-011", barcode="PRD34567", name="Механическая клавиатура", price=7990, stock=6, location="B-02-01", category_id=3, description="brand:Logitech|country:Тайвань|category:Computer Accessories|weight:1.2kg|dimensions:45x15cm"),
                Product(sku="PRD-012", barcode="PRD45678", name="Кофеварка", price=15990, stock=3, location="C-02-01", category_id=1, description="brand:DeLonghi|country:Италия|category:Kitchen Appliances|weight:4kg|dimensions:30x25cm"),
            ]
            db.add_all(products)
            
            zones = [
                WarehouseZone(code="A", name="Электроника", capacity=1000, used=750),
                WarehouseZone(code="B", name="Бытовая техника", capacity=800, used=600),
                WarehouseZone(code="C", name="Одежда", capacity=1200, used=400),
                WarehouseZone(code="D", name="Продукты", capacity=500, used=480),
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
async def lifespan(app: FastAPI):
    init_database()
    print(f"[{SERVICE_NAME}] Starting on port {SERVICE_PORT}...")
    yield
    print(f"[{SERVICE_NAME}] Shutting down...")


app = FastAPI(
    title="Product Service",
    description="Микросервис управления товарами WMS",
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

@app.get("/products")
def get_products(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Список товаров"""
    query = db.query(Product)
    
    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") |
            Product.sku.ilike(f"%{search}%")
        )
    if category:
        query = query.filter(Product.category_id == category)
    
    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return {
        "data": [ProductResponse.model_validate(p) for p in products],
        "meta": {"page": page, "limit": limit, "total": total}
    }


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Получить товар"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """Создать товар"""
    if db.query(Product).filter(Product.sku == data.sku.strip()).first():
        raise HTTPException(status_code=409, detail="Такой артикул уже есть")
    barcode = f"400{random.randint(1000000000, 9999999999)}"
    location = f"A-0{random.randint(1, 9)}-0{random.randint(1, 9)}"
    
    product = Product(
        sku=data.sku,
        barcode=barcode,
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        location=location
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    print(f"[{SERVICE_NAME}] Product {data.sku} created")
    
    return ProductResponse.model_validate(product)


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Удалить товар"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    
    print(f"[{SERVICE_NAME}] Product {product_id} deleted")


@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Список категорий"""
    return db.query(Category).filter(Category.is_active == True).all()


@app.get("/zones")
def get_zones(db: Session = Depends(get_db)):
    """Список зон склада"""
    return db.query(WarehouseZone).filter(WarehouseZone.is_active == True).all()


# ==================== Internal API (для Order Service) ====================

@app.post("/internal/reserve")
def reserve_products(
    data: ReserveRequest,
    _: bool = Depends(verify_internal_key),
    db: Session = Depends(get_db)
):
    """
    Резервирование товаров (внутренний API).
    Вызывается Order Service при создании заказа.
    """
    reserved_items = []
    
    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue
        
        available = product.stock - product.reserved
        if available >= item.quantity:
            product.reserved += item.quantity
            reserved_items.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "reserved": True
            })
        else:
            reserved_items.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "reserved": False,
                "available": available
            })
    
    db.commit()
    
    print(f"[{SERVICE_NAME}] Reserved {len([i for i in reserved_items if i.get('reserved')])} items")
    
    return {"items": reserved_items}


@app.post("/internal/release")
def release_products(
    data: ReserveRequest,
    _: bool = Depends(verify_internal_key),
    db: Session = Depends(get_db)
):
    """
    Освобождение резерва (внутренний API).
    Вызывается при отмене заказа.
    """
    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.reserved = max(0, product.reserved - item.quantity)
    
    db.commit()
    
    print(f"[{SERVICE_NAME}] Released reserve for {len(data.items)} items")
    
    return {"status": "released"}


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
