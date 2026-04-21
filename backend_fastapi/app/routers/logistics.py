import random
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, required_roles
from app.models import Carrier, Order, Shipment, User

router = APIRouter(prefix="/logistics", tags=["logistics"])

write_log = required_roles("admin", "manager")


class ShipmentCreateIn(BaseModel):
    order_id: int
    carrier_id: int
    delivery_method: str = Field(..., pattern="^(courier|pickup|post)$")


@router.get("/shipments")
def list_shipments(
    _: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = db.query(Shipment, Order, Carrier).join(Order, Shipment.order_id == Order.id).join(Carrier, Shipment.carrier_id == Carrier.id)
    out = []
    for s, o, c in rows.order_by(Shipment.id.desc()).all():
        out.append(
            {
                "id": s.id,
                "order_id": o.id,
                "order_number": o.order_number,
                "tracking_number": s.tracking_number,
                "carrier_name": c.name,
                "delivery_method": s.delivery_method,
                "status": s.status,
                "recipient_name": s.recipient_name,
                "delivery_address": s.delivery_address,
                "estimated_delivery": s.estimated_delivery or "",
                "created_at": s.created_at.isoformat(),
            }
        )
    return out


@router.get("/carriers")
def carriers(
    _: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return [{"id": c.id, "name": c.name} for c in db.query(Carrier).order_by(Carrier.id).all()]


@router.get("/stats")
def shipment_stats(_: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)) -> dict[str, int]:
    total = db.query(Shipment).count()
    pending = db.query(Shipment).filter(Shipment.status == "pending").count()
    it = db.query(Shipment).filter(Shipment.status == "in_transit").count()
    delivered = db.query(Shipment).filter(Shipment.status == "delivered").count()
    return {"total": total, "pending": pending, "in_transit": it, "delivered": delivered}


@router.post("/shipments")
def create_shipment(
    body: ShipmentCreateIn,
    _: Annotated[User, Depends(write_log)],
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    o = db.get(Order, body.order_id)
    if not o:
        raise HTTPException(404, detail="Заказ не найден")
    if o.status != "picking":
        raise HTTPException(400, detail="Отправление создаётся только для заказа в сборке")

    carrier = db.get(Carrier, body.carrier_id)
    if not carrier:
        raise HTTPException(400, detail="Неизвестный перевозчик")

    if not o.shipping_ready:
        raise HTTPException(409, detail="Сначала завершите сборку по заказу")

    if db.query(Shipment).filter(Shipment.order_id == o.id).first():
        raise HTTPException(409, detail="На этот заказ уже есть отправление")

    track = f"TRK-{random.randint(100000,999999)}"
    eta = datetime.now(UTC) + timedelta(days=3)
    s = Shipment(
        order_id=o.id,
        carrier_id=carrier.id,
        tracking_number=track,
        delivery_method=body.delivery_method,
        status="pending",
        recipient_name=o.customer_name,
        delivery_address=o.customer_address,
        estimated_delivery=f"{eta:%d.%m.%Y}",
        created_at=datetime.now(UTC),
    )
    o.status = "shipped"
    o.shipping_ready = False
    o.updated_at = datetime.now(UTC)
    db.add(s)
    db.add(o)
    db.commit()
    db.refresh(s)
    db.refresh(carrier)
    return {
        "id": s.id,
        "tracking_number": s.tracking_number,
        "order_number": o.order_number,
        "carrier_name": carrier.name,
        "status": s.status,
    }
