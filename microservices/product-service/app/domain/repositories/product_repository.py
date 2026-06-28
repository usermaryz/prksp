from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.product import Product


class ProductRepository(ABC):

    @abstractmethod
    def find_by_id(self, product_id: int) -> Optional[Product]:
        ...

    @abstractmethod
    def find_by_sku(self, sku: str) -> Optional[Product]:
        ...

    @abstractmethod
    def find_all(
        self,
        search: Optional[str] = None,
        category: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Product]:
        ...

    @abstractmethod
    def save(self, product: Product) -> Product:
        ...

    @abstractmethod
    def delete(self, product_id: int) -> None:
        ...

    @abstractmethod
    def count(
        self,
        search: Optional[str] = None,
        category: Optional[int] = None,
    ) -> int:
        ...
