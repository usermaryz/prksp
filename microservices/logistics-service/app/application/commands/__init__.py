from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateShipmentCommand:
    order_id: int
    carrier_id: int
    delivery_method: str


@dataclass(frozen=True)
class CreateShipmentInternalCommand:
    order_id: int
    order_number: Optional[str]
    recipient_name: Optional[str]
    recipient_phone: Optional[str]
    delivery_address: Optional[str]
