from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ..events.product_events import DomainEvent, ProductCreatedEvent, StockReservedEvent, StockReleasedEvent
from ..value_objects.price import Price
from ..value_objects.product_status import ProductStatus


@dataclass
class Product:
    id: Optional[int]
    sku: str
    barcode: str
    name: str
    description: Optional[str]
    price: Decimal
    category_id: Optional[int]
    status: ProductStatus
    stock: int
    reserved: int
    location: Optional[str]
    created_at: datetime
    updated_at: datetime
    _events: List[DomainEvent] = field(default_factory=list, repr=False, compare=False)

    @classmethod
    def create(
        cls,
        sku: str,
        barcode: str,
        name: str,
        description: Optional[str],
        price: Decimal,
        stock: int,
        location: Optional[str],
        category_id: Optional[int] = None,
    ) -> Product:
        now = datetime.utcnow()
        product = cls(
            id=None,
            sku=sku,
            barcode=barcode,
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            status=ProductStatus.active,
            stock=stock,
            reserved=0,
            location=location,
            created_at=now,
            updated_at=now,
        )
        product._add_event(ProductCreatedEvent(product_id=None, sku=sku, name=name))

        return product

    @property
    def available_stock(self) -> int:
        return self.stock - self.reserved

    def reserve(self, qty: int) -> None:
        if qty > self.available_stock:
            raise ValueError(
                f"Cannot reserve {qty}: only {self.available_stock} available"
            )
        self.reserved += qty
        self.updated_at = datetime.utcnow()
        self._add_event(StockReservedEvent(product_id=self.id, quantity=qty))

    def release_reservation(self, qty: int) -> None:
        self.reserved = max(0, self.reserved - qty)
        self.updated_at = datetime.utcnow()
        self._add_event(StockReleasedEvent(product_id=self.id, quantity=qty))

    def update_stock(self, qty: int) -> None:
        self.stock = qty
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        self.status = ProductStatus.inactive
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        self.status = ProductStatus.active
        self.updated_at = datetime.utcnow()

    def update_details(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[Decimal] = None,
        stock: Optional[int] = None,
        location: Optional[str] = None,
        status: Optional[ProductStatus] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if price is not None:
            self.price = price
        if stock is not None:
            self.stock = stock
        if location is not None:
            self.location = location
        if status is not None:
            self.status = status
        self.updated_at = datetime.utcnow()

    @staticmethod
    def merge_wms_status(description: Optional[str], workflow_status: str) -> str:
        parts = [p for p in (description or "").split("|") if p and not p.startswith("wms_status:")]
        parts.append(f"wms_status:{workflow_status}")
        return "|".join(parts)

    def collect_events(self) -> List[DomainEvent]:
        events = list(self._events)
        self._events.clear()

        return events

    def _add_event(self, event: DomainEvent) -> None:
        self._events.append(event)
