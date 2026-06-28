from __future__ import annotations

import random
from decimal import Decimal
from typing import Any, Dict, List, Optional

from ...domain.entities.product import Product
from ...domain.repositories.product_repository import ProductRepository
from ...domain.value_objects.product_status import ProductStatus


class ProductApplicationService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def create_product(
        self,
        sku: str,
        name: str,
        description: Optional[str],
        price: Optional[Decimal],
        stock: int,
    ) -> Product:
        barcode = f"400{random.randint(1000000000, 9999999999)}"
        location = f"A-0{random.randint(1, 9)}-0{random.randint(1, 9)}"
        product = Product.create(
            sku=sku,
            barcode=barcode,
            name=name,
            description=description,
            price=price or Decimal("0"),
            stock=stock,
            location=location,
        )
        saved = self._repository.save(product)

        return saved

    def get_product(self, product_id: int) -> Optional[Product]:
        return self._repository.find_by_id(product_id)

    def list_products(
        self,
        search: Optional[str] = None,
        category: Optional[int] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        offset = (page - 1) * limit
        products = self._repository.find_all(
            search=search,
            category=category,
            limit=limit,
            offset=offset,
        )
        total = self._repository.count(search=search, category=category)

        return {
            "items": products,
            "total": total,
            "page": page,
            "limit": limit,
        }

    def delete_product(self, product_id: int) -> bool:
        product = self._repository.find_by_id(product_id)
        if product is None:
            return False
        self._repository.delete(product_id)

        return True

    def reserve_stock(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        for item in items:
            product = self._repository.find_by_id(item["product_id"])
            if product is None:
                continue
            try:
                product.reserve(item["quantity"])
                self._repository.save(product)
                result.append({
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "reserved": True,
                })
            except ValueError:
                result.append({
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "reserved": False,
                    "available": product.available_stock,
                })

        return result

    def release_stock(self, items: List[Dict[str, Any]]) -> Dict[str, str]:
        for item in items:
            product = self._repository.find_by_id(item["product_id"])
            if product is None:
                continue
            product.release_reservation(item["quantity"])
            self._repository.save(product)

        return {"status": "released"}

    def update_product(
        self,
        product_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[Decimal] = None,
        stock: Optional[int] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[Product]:
        product = self._repository.find_by_id(product_id)
        if product is None:
            return None

        parsed_status: Optional[ProductStatus] = None
        if status is not None:
            try:
                parsed_status = ProductStatus(status)
            except ValueError:
                description = Product.merge_wms_status(
                    description if description is not None else product.description,
                    status,
                )

        product.update_details(
            name=name,
            description=description,
            price=price,
            stock=stock,
            location=location,
            status=parsed_status,
        )
        return self._repository.save(product)
