from datetime import UTC, datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, required_roles
from app.models import Order, PickingTask, User

router = APIRouter(prefix="/orders", tags=["orders"])

OrderStatus = Literal["pending", "picking", "shipped", "delivered"]

can_read_orders = required_roles("admin", "manager", "picker", "driver")


class OrderRow(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_phone: str | None = None
    customer_address: str | None = None
    status: str
    priority: str
    total: float
    items_count: int
    created_at: datetime


class OrderCreateIn(BaseModel):
    customer_name: str = Field(..., max_length=255)
    customer_phone: str = Field("", max_length=64)
    customer_address: str = Field("", max_length=512)


def _serialize(o: Order) -> dict[str, Any]:
    return {
        "id": o.id,
        "order_number": o.order_number,
        "customer_name": o.customer_name,
        "customer_phone": o.customer_phone,
        "customer_address": o.customer_address,
        "status": o.status,
        "priority": o.priority,
        "total": float(o.total),
        "items_count": int(o.items_count),
        "created_at": o.created_at.isoformat(),
    }


def _next_order_number(db: Session) -> str:
    mx = db.query(Order).count()
    return f"ORD-2026-{mx + 1:03d}"


def ensure_picking_task(db: Session, order: Order) -> None:
    has = db.query(PickingTask).filter(PickingTask.order_id == order.id).first()
    if has:
        return
    db.add(
        PickingTask(
            order_id=order.id,
            status="pending",
            assigned_to=None,
            progress=0,
            items_count=max(1, order.items_count),
            created_at=datetime.now(UTC),
            completed_at=None,
        )
    )


@router.get("")
def list_orders(
    _: Annotated[User, Depends(can_read_orders)],
    db: Session = Depends(get_db),
    status: str | None = None,
    ready_for_shipping: bool | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=300),
) -> dict[str, Any]:
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status.strip())
    if ready_for_shipping:
        q = q.filter(Order.shipping_ready.is_(True), Order.status == "picking")

    total = q.count()
    orders = (
        q.order_by(Order.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    tp = max(1, (total + limit - 1) // limit)
    return {
        "data": [_serialize(o) for o in orders],
        "meta": {"page": page, "limit": limit, "total": total, "total_pages": tp},
    }


@router.post("", status_code=201)
def create_order(
    body: OrderCreateIn,
    _: Annotated[User, Depends(required_roles("admin", "manager"))],
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    now = datetime.now(UTC)
    o = Order(
        order_number=_next_order_number(db),
        customer_name=body.customer_name.strip(),
        customer_phone=(body.customer_phone or "").strip(),
        customer_address=(body.customer_address or "").strip(),
        status="pending",
        priority="normal",
        total=0.0,
        items_count=1,
        shipping_ready=False,
        created_at=now,
        updated_at=now,
    )
    db.add(o)
    db.commit()
    db.refresh(o)
    return _serialize(o)


@router.patch("/{order_id}/status")
def update_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    o = db.get(Order, order_id)
    if not o:
        raise HTTPException(404, detail="Заказ не найден")

    if user.role == "picker":
        if status != "picking":
            raise HTTPException(403, detail="Сборщик может перевести заказ только в статус «сборка»")
        if o.status != "pending":
            raise HTTPException(400, detail="В сборку можно отправить только заказ в статусе «ожидает»")
    elif status in {"shipped", "delivered", "pending"} and user.role not in {"admin", "manager"}:
        raise HTTPException(403, detail="Недостаточно прав для выбранного статуса")

    o.status = status
    o.updated_at = datetime.now(UTC)
    o.shipping_ready = False

    if status == "picking":
        ensure_picking_task(db, o)
        for t in db.query(PickingTask).filter(PickingTask.order_id == o.id).all():
            if t.status != "completed":
                t.completed_at = None

    db.add(o)
    db.commit()
    db.refresh(o)
    return _serialize(o)
