from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..domain.entities.order import Order
from ..domain.repositories.order_repository import OrderRepository
from ..domain.value_objects import OrderStatusEnum
from .services.order_application_service import CreateOrderDTO, OrderApplicationService


@dataclass
class CreateOrderUseCase:
    repo: OrderRepository

    def execute(
        self,
        customer_name: str,
        customer_phone: str,
        customer_email: Optional[str] = None,
        customer_address: Optional[str] = None,
        total: float = 0.0,
    ) -> Order:
        service = OrderApplicationService(self.repo, event_publisher=lambda e: None)
        dto = CreateOrderDTO(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            customer_address=customer_address,
        )
        created = service.create_order(dto)
        service.change_status(created.id, OrderStatusEnum.CONFIRMED)
        entity = self.repo.find_by_id(created.id)
        if not entity:
            raise RuntimeError("Order not found after create")
        return entity
