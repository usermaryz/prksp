from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AddItemCommand:
    order_id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_price: float
