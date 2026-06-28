from __future__ import annotations

from ..commands import (
    CreateProductCommand,
    DeleteProductCommand,
    ReserveStockCommand,
    ReleaseStockCommand,
    UpdateProductCommand,
)
from ..services.product_application_service import ProductApplicationService


def handle_create_product(command: CreateProductCommand, service: ProductApplicationService):
    return service.create_product(
        sku=command.sku,
        name=command.name,
        description=command.description,
        price=command.price,
        stock=command.stock,
    )


def handle_delete_product(command: DeleteProductCommand, service: ProductApplicationService) -> bool:
    return service.delete_product(command.product_id)


def handle_reserve_stock(command: ReserveStockCommand, service: ProductApplicationService):
    return service.reserve_stock(list(command.items))


def handle_release_stock(command: ReleaseStockCommand, service: ProductApplicationService):
    return service.release_stock(list(command.items))


def handle_update_product(command: UpdateProductCommand, service: ProductApplicationService):
    return service.update_product(
        product_id=command.product_id,
        name=command.name,
        description=command.description,
        price=command.price,
        stock=command.stock,
        location=command.location,
        status=command.status,
    )
