from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PickingTaskModel(Base):
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
