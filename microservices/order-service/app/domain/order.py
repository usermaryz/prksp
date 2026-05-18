from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .entities.order import Order as OrderAggregate
from .value_objects import OrderStatusEnum


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"


@dataclass
class Order:
    id: int | None
    order_number: str
    customer_id: int | None
    status: OrderStatus
    total: float

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError("Can only confirm pending orders")
        self.status = OrderStatus.CONFIRMED

    @classmethod
    def from_aggregate(cls, order: OrderAggregate, customer_id: int | None = None) -> Order:
        status_val = order.status.value.value
        mapped = OrderStatus.PENDING
        if status_val == "confirmed":
            mapped = OrderStatus.CONFIRMED
        elif status_val in ("shipped", "delivered"):
            mapped = OrderStatus.SHIPPED
        return cls(
            id=order.id,
            order_number=order.order_number,
            customer_id=customer_id,
            status=mapped,
            total=float(order.total.amount),
        )
