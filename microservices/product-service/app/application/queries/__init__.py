from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GetProductQuery:
    product_id: int


@dataclass(frozen=True)
class ListProductsQuery:
    page: int = 1
    limit: int = 20
    search: Optional[str] = None
    category: Optional[int] = None


@dataclass(frozen=True)
class ListCategoriesQuery:
    pass


@dataclass(frozen=True)
class ListZonesQuery:
    pass


__all__ = [
    "GetProductQuery",
    "ListProductsQuery",
    "ListCategoriesQuery",
    "ListZonesQuery",
]
