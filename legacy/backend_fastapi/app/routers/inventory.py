from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User, WarehouseZone

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/zones")
def zones(_: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    z = db.query(WarehouseZone).order_by(WarehouseZone.code).all()
    return [
        {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "capacity": row.capacity,
            "used": row.used,
        }
        for row in z
    ]
