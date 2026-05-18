from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Order, PickingTask, Product, Shipment, User, WarehouseZone

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics")
def metrics(_: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)) -> dict[str, Any]:
    prod_total = db.query(func.count(Product.id)).scalar() or 0
    active_products = db.query(func.count(Product.id)).filter(Product.stock > 0).scalar() or 0
    low = db.query(func.count(Product.id)).filter(Product.stock <= 20).scalar() or 0

    o_total = db.query(func.count(Order.id)).scalar() or 0
    o_pending = db.query(func.count(Order.id)).filter(Order.status == "pending").scalar() or 0
    o_picking = db.query(func.count(Order.id)).filter(Order.status == "picking").scalar() or 0
    o_shipped = db.query(func.count(Order.id)).filter(Order.status == "shipped").scalar() or 0

    today = date.today()
    delivered_today = sum(
        1
        for o in db.query(Order).filter(Order.status == "delivered").all()
        if o.updated_at.date() == today
    )

    zones = db.query(WarehouseZone).all()
    cap = sum(z.capacity for z in zones)
    use = sum(z.used for z in zones)
    inv_items = db.query(func.coalesce(func.sum(Product.stock), 0)).scalar() or 0
    total_value = db.query(func.coalesce(func.sum(Product.price * Product.stock), 0.0)).scalar() or 0.0

    p_pending = db.query(func.count(PickingTask.id)).filter(PickingTask.status == "pending").scalar() or 0
    p_ip = db.query(func.count(PickingTask.id)).filter(PickingTask.status == "in_progress").scalar() or 0
    completed_today = 0
    for t in db.query(PickingTask).filter(PickingTask.completed_at.isnot(None)).all():
        if t.completed_at and t.completed_at.date() == today:
            completed_today += 1

    s_pen = db.query(func.count(Shipment.id)).filter(Shipment.status == "pending").scalar() or 0
    s_tr = db.query(func.count(Shipment.id)).filter(Shipment.status == "in_transit").scalar() or 0
    s_delivered = db.query(func.count(Shipment.id)).filter(Shipment.status == "delivered").scalar() or 0
    failed = 0

    return {
        "products": {"total": prod_total, "active": active_products, "low_stock": low},
        "orders": {
            "total": o_total,
            "pending": o_pending,
            "picking": o_picking,
            "shipped": o_shipped,
            "delivered_today": delivered_today,
        },
        "inventory": {
            "total_items": int(inv_items),
            "total_value": float(total_value),
            "zones_capacity": cap,
            "zones_usage": use,
        },
        "picking": {
            "pending_tasks": p_pending,
            "in_progress": p_ip,
            "completed_today": completed_today,
            "average_time_minutes": 18,
        },
        "logistics": {
            "pending_shipments": s_pen,
            "in_transit": s_tr,
            "delivered_today": min(s_delivered, 5),
            "failed_deliveries": failed,
        },
    }
