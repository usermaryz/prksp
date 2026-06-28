from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WarehouseZone(Base):
    __tablename__ = "warehouse_zones"

    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String)
    zone_type = Column(String(20), default="storage")
    capacity = Column(Integer, default=1000)
    current_usage = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StorageLocation(Base):
    __tablename__ = "storage_locations"

    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("warehouse_zones.id"))
    code = Column(String(20), unique=True, nullable=False)
    aisle = Column(String(10))
    rack = Column(String(10))
    shelf = Column(String(10))
    bin = Column(String(10))
    location_type = Column(String(20), default="bulk")
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    location_id = Column(Integer, ForeignKey("storage_locations.id"))
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    lot_number = Column(String(50))
    expiry_date = Column(Date)
    received_at = Column(DateTime, default=datetime.utcnow)
    last_counted_at = Column(DateTime)


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    from_location_id = Column(Integer, ForeignKey("storage_locations.id"))
    to_location_id = Column(Integer, ForeignKey("storage_locations.id"))
    quantity = Column(Integer, nullable=False)
    movement_type = Column(String(20))
    reason = Column(String)
    performed_by = Column(Integer)
    performed_at = Column(DateTime, default=datetime.utcnow)
