from __future__ import annotations

from ..commands import CreateShipmentCommand, CreateShipmentInternalCommand
from ..services.logistics_application_service import LogisticsApplicationService, ShipmentDTO


def handle_create_shipment(
    command: CreateShipmentCommand,
    service: LogisticsApplicationService,
) -> ShipmentDTO:
    return service.create_shipment(
        order_id=command.order_id,
        carrier_id=command.carrier_id,
        delivery_method=command.delivery_method,
    )


def handle_create_shipment_internal(
    command: CreateShipmentInternalCommand,
    service: LogisticsApplicationService,
) -> ShipmentDTO:
    return service.create_shipment_internal(
        order_id=command.order_id,
        order_number=command.order_number,
        recipient_name=command.recipient_name,
        recipient_phone=command.recipient_phone,
        delivery_address=command.delivery_address,
    )
