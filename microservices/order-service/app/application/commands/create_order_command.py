from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class OrderItemData:
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_price: float


@dataclass(frozen=True)
class CreateOrderCommand:
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    priority: str = "normal"
    notes: Optional[str] = None
    items: List[OrderItemData] = field(default_factory=list)
