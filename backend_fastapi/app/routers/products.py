from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import required_roles
from app.models import Product, User

router = APIRouter(prefix="/products", tags=["products"])

admin_manager = required_roles("admin", "manager")


class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., max_length=255)
    price: float = Field(..., ge=0)
    stock: int = Field(0, ge=0)
    description: str | None = None


class ProductRow(BaseModel):
    id: int
    sku: str
    name: str
    description: str | None
    price: float
    stock: int
    location: str | None
    category_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("")
def list_products(
    _: Annotated[User, Depends(admin_manager)],
    db: Session = Depends(get_db),
    search: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
) -> dict[str, Any]:
    q = db.query(Product)
    if search:
        s = f"%{search.strip()}%"
        q = q.filter(or_(Product.name.ilike(s), Product.sku.ilike(s)))

    total = q.count()
    rows = (
        q.order_by(Product.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    payload = []
    for p in rows:
        payload.append(
            {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "description": p.description,
                "price": float(p.price),
                "stock": int(p.stock),
                "location": p.location,
                "category_id": p.category_id,
                "created_at": p.created_at.isoformat(),
            }
        )
    tp = max(1, (total + limit - 1) // limit)
    return {
        "data": payload,
        "meta": {"page": page, "limit": limit, "total": total, "total_pages": tp},
    }


@router.post("", status_code=201)
def create_product(
    body: ProductCreate,
    _: Annotated[User, Depends(admin_manager)],
    db: Session = Depends(get_db),
) -> ProductRow:
    if db.query(Product).filter(Product.sku == body.sku.strip()).first():
        raise HTTPException(409, detail="Такой артикул уже есть")

    now = datetime.now(UTC)
    p = Product(
        sku=body.sku.strip(),
        barcode=(body.sku.strip().replace("/", "-")),
        name=body.name.strip(),
        description=body.description,
        price=float(body.price),
        stock=int(body.stock),
        location=None,
        category_id=None,
        created_at=now,
        updated_at=now,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return ProductRow.model_validate(p)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    _: Annotated[User, Depends(admin_manager)],
    db: Session = Depends(get_db),
) -> dict[str, str]:
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(404, detail="Товар не найден")
    db.delete(p)
    db.commit()
    return {"status": "deleted"}
