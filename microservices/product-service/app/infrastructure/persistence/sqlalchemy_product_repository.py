from __future__ import annotations

import json
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities.product import Product
from ...domain.repositories.product_repository import ProductRepository
from ...domain.value_objects.product_status import ProductStatus
from ..redis_client import get_redis
from .models import ProductModel


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def find_by_id(self, product_id: int) -> Optional[Product]:
        model = self._db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model is None:
            return None

        return self._to_entity(model)

    def find_by_sku(self, sku: str) -> Optional[Product]:
        model = self._db.query(ProductModel).filter(ProductModel.sku == sku).first()
        if model is None:
            return None

        return self._to_entity(model)

    def find_all(
        self,
        search: Optional[str] = None,
        category: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Product]:
        query = self._db.query(ProductModel)
        if search:
            query = query.filter(
                ProductModel.name.ilike(f"%{search}%")
                | ProductModel.sku.ilike(f"%{search}%")
            )
        if category is not None:
            query = query.filter(ProductModel.category_id == category)
        models = query.order_by(ProductModel.created_at.desc()).offset(offset).limit(limit).all()

        return [self._to_entity(m) for m in models]

    def save(self, product: Product) -> Product:
        r = get_redis()
        if product.id is None:
            model = self._to_model(product)
            self._db.add(model)
            self._db.commit()
            self._db.refresh(model)
            product.id = model.id
        else:
            model = self._db.query(ProductModel).filter(ProductModel.id == product.id).first()
            if model is None:
                model = self._to_model(product)
                self._db.add(model)
            else:
                self._apply_to_model(product, model)
            self._db.commit()
            self._db.refresh(model)
            r.delete(f"product:{product.id}")

        return self._to_entity(model)

    def delete(self, product_id: int) -> None:
        model = self._db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model is not None:
            self._db.delete(model)
            self._db.commit()
        get_redis().delete(f"product:{product_id}")

    def count(
        self,
        search: Optional[str] = None,
        category: Optional[int] = None,
    ) -> int:
        query = self._db.query(ProductModel)
        if search:
            query = query.filter(
                ProductModel.name.ilike(f"%{search}%")
                | ProductModel.sku.ilike(f"%{search}%")
            )
        if category is not None:
            query = query.filter(ProductModel.category_id == category)

        return query.count()

    def _parse_status(self, raw: str | None) -> ProductStatus:
        if not raw:
            return ProductStatus.active
        try:
            return ProductStatus(raw)
        except ValueError:
            # Legacy / UI workflow values (processing, completed, rejected) → active
            return ProductStatus.active

    def _to_entity(self, model: ProductModel) -> Product:
        return Product(
            id=model.id,
            sku=model.sku,
            barcode=model.barcode,
            name=model.name,
            description=model.description,
            price=Decimal(str(model.price)) if model.price is not None else Decimal("0"),
            category_id=model.category_id,
            status=self._parse_status(model.status),
            stock=model.stock or 0,
            reserved=model.reserved or 0,
            location=model.location,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, product: Product) -> ProductModel:
        return ProductModel(
            sku=product.sku,
            barcode=product.barcode,
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            status=product.status.value,
            stock=product.stock,
            reserved=product.reserved,
            location=product.location,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    def _apply_to_model(self, product: Product, model: ProductModel) -> None:
        model.sku = product.sku
        model.barcode = product.barcode
        model.name = product.name
        model.description = product.description
        model.price = product.price
        model.category_id = product.category_id
        model.status = product.status.value
        model.stock = product.stock
        model.reserved = product.reserved
        model.location = product.location
        model.updated_at = product.updated_at
