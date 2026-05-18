"""
SQLAlchemy ORM Models
=====================

Модели базы данных для Order Service.

Это НЕ Domain Entities!
Модели используются только в Infrastructure Layer
для маппинга данных в/из базы.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class OrderModel(Base):
    """
    ORM модель заказа.
    
    Маппится на таблицу orders.
    Используется SQLAlchemyOrderRepository для конвертации в Domain Entity.
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Customer info
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(255))
    customer_address = Column(Text)
    
    # Status & Priority
    status = Column(String(20), default="pending", index=True)
    priority = Column(String(10), default="normal")
    
    # Calculated fields (denormalized for performance)
    total = Column(Numeric(12, 2), default=0)
    items_count = Column(Integer, default=0)
    
    # Metadata
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    items = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="joined"  # Eager loading для избежания N+1
    )


class OrderItemModel(Base):
    """
    ORM модель позиции заказа.
    
    Маппится на таблицу order_items.
    """
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    
    # Product info (денормализовано для независимости от Product Service)
    product_id = Column(Integer, nullable=False, index=True)
    product_sku = Column(String(50))
    product_name = Column(String(255))
    
    # Quantity & Price
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2))
    total_price = Column(Numeric(12, 2))
    
    # Relations
    order = relationship("OrderModel", back_populates="items")



