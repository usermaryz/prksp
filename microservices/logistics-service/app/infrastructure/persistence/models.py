from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ShipmentModel(Base):
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


class CarrierModel(Base):
    __tablename__ = "carriers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Integer, default=1)
