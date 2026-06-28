from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class InventoryItem:
    id: Optional[int]
    product_id: int
    location_id: int
    quantity: int
    reserved_quantity: int
    lot_number: Optional[str]
    expiry_date: Optional[date]
    received_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity

    def add_stock(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError(f"Quantity to add must be positive, got {qty}")
        self.quantity += qty

    def remove_stock(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError(f"Quantity to remove must be positive, got {qty}")
        if self.quantity - qty < 0:
            raise ValueError(
                f"Insufficient stock: available={self.quantity}, requested={qty}"
            )
        self.quantity -= qty

    def reserve(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError(f"Reservation quantity must be positive, got {qty}")
        if self.available_quantity < qty:
            raise ValueError(
                f"Insufficient available stock: available={self.available_quantity}, requested={qty}"
            )
        self.reserved_quantity += qty

    def release_reservation(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError(f"Release quantity must be positive, got {qty}")
        if self.reserved_quantity - qty < 0:
            raise ValueError(
                f"Cannot release more than reserved: reserved={self.reserved_quantity}, releasing={qty}"
            )
        self.reserved_quantity -= qty
