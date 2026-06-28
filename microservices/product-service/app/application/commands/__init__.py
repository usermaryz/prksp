from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass(frozen=True)
class CreateProductCommand:
    sku: str
    name: str
    description: str | None
    price: Decimal | None
    stock: int


@dataclass(frozen=True)
class DeleteProductCommand:
    product_id: int


@dataclass(frozen=True)
class ReserveStockCommand:
    items: tuple


@dataclass(frozen=True)
class ReleaseStockCommand:
    items: tuple


@dataclass(frozen=True)
class UpdateProductCommand:
    product_id: int
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    location: str | None = None
    status: str | None = None


__all__ = [
    "CreateProductCommand",
    "DeleteProductCommand",
    "ReserveStockCommand",
    "ReleaseStockCommand",
    "UpdateProductCommand",
]
