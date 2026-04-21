from datetime import UTC, date, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import required_roles
from app.models import Order, PickingTask, User

router = APIRouter(prefix="/picking", tags=["picking"])

pick_roles = required_roles("admin", "manager", "picker")


@router.get("/tasks")
def tasks(
    _: Annotated[User, Depends(pick_roles)],
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = db.query(PickingTask, Order).join(Order, PickingTask.order_id == Order.id).order_by(PickingTask.id).all()
    out: list[dict[str, Any]] = []
    for t, o in rows:
        out.append(
            {
                "id": t.id,
                "order_id": o.id,
                "order_number": o.order_number,
                "status": t.status,
                "priority": o.priority,
                "assigned_to": t.assigned_to,
                "progress": t.progress,
                "items_count": t.items_count,
                "created_at": t.created_at.isoformat(),
            }
        )
    return out


@router.get("/stats")
def stats(
    _: Annotated[User, Depends(pick_roles)],
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    today = date.today()
    pending = db.query(PickingTask).filter(PickingTask.status == "pending").count()
    prog = db.query(PickingTask).filter(PickingTask.status == "in_progress").count()
    done_today = 0
    for t in db.query(PickingTask).filter(PickingTask.completed_at.isnot(None)).all():
        if t.completed_at and t.completed_at.date() == today:
            done_today += 1
    return {
        "pending": pending,
        "in_progress": prog,
        "completed_today": done_today,
        "average_time_minutes": 18,
        "pending_tasks": pending,
    }


@router.post("/tasks/{task_id}/start")
def start_task(
    task_id: int,
    user: Annotated[User, Depends(pick_roles)],
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    t = db.get(PickingTask, task_id)
    if not t:
        raise HTTPException(404, detail="Задача не найдена")
    if t.status == "completed":
        raise HTTPException(400, detail="Задача уже завершена")

    o = db.get(Order, t.order_id)
    if not o:
        raise HTTPException(400, detail="Нет заказа")

    if o.status not in {"picking"}:
        raise HTTPException(400, detail="Заказ должен быть в статусе «сборка»")

    t.status = "in_progress"
    t.assigned_to = user.full_name
    t.progress = max(t.progress, 40)
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id, "status": t.status, "progress": t.progress}


@router.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    _: Annotated[User, Depends(pick_roles)],
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    t = db.get(PickingTask, task_id)
    if not t:
        raise HTTPException(404, detail="Задача не найдена")
    o = db.get(Order, t.order_id)
    if not o:
        raise HTTPException(400, detail="Нет заказа")

    t.status = "completed"
    t.progress = 100
    t.completed_at = datetime.now(UTC)
    o.shipping_ready = True
    o.updated_at = datetime.now(UTC)
    db.add(t)
    db.add(o)
    db.commit()
    return {"id": t.id, "status": t.status}
