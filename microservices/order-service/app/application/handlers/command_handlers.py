"""Command handlers — all state-mutating operations live here."""
from __future__ import annotations

from ..commands import (
    AddItemCommand,
    CancelOrderCommand,
    ChangeStatusCommand,
    CreateOrderCommand,
)
from ..services.order_application_service import (
    AddItemDTO,
    CreateOrderDTO,
    OrderApplicationService,
    OrderDTO,
)


def handle_create_order(command: CreateOrderCommand, service: OrderApplicationService) -> OrderDTO:
    dto = CreateOrderDTO(
        customer_name=command.customer_name,
        customer_phone=command.customer_phone,
        customer_email=command.customer_email,
        customer_address=command.customer_address,
        priority=command.priority,
        notes=command.notes,
    )
    order = service.create_order(dto)
    for item in command.items:
        order = service.add_item(
            order.id,
            AddItemDTO(
                product_id=item.product_id,
                product_name=item.product_name,
                product_sku=item.product_sku,
                quantity=item.quantity,
                unit_price=item.unit_price,
            ),
        )

    return order


def handle_change_status(command: ChangeStatusCommand, service: OrderApplicationService) -> OrderDTO:
    return service.change_status(command.order_id, command.new_status)


def handle_add_item(command: AddItemCommand, service: OrderApplicationService) -> OrderDTO:
    dto = AddItemDTO(
        product_id=command.product_id,
        product_name=command.product_name,
        product_sku=command.product_sku,
        quantity=command.quantity,
        unit_price=command.unit_price,
    )

    return service.add_item(command.order_id, dto)


def handle_cancel_order(command: CancelOrderCommand, service: OrderApplicationService) -> OrderDTO:
    return service.cancel_order(command.order_id, command.reason)
