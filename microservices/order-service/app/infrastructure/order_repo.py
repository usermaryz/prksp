from typing import List, Optional

from sqlalchemy.orm import Session

from ..domain.entities.order import Order
from ..domain.repositories.order_repository import OrderRepository
from ..domain.value_objects import OrderStatusEnum
from .persistence.sqlalchemy_order_repository import SQLAlchemyOrderRepository


class SQLOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self._impl = SQLAlchemyOrderRepository(session)

    def save(self, order: Order) -> Order:
        return self._impl.save(order)

    def find_by_id(self, order_id: int) -> Optional[Order]:
        return self._impl.find_by_id(order_id)

    def find_by_order_number(self, order_number: str) -> Optional[Order]:
        return self._impl.find_by_order_number(order_number)

    def find_all(
        self,
        status: Optional[OrderStatusEnum] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Order]:
        return self._impl.find_all(status=status, limit=limit, offset=offset)

    def count(self, status: Optional[OrderStatusEnum] = None) -> int:
        return self._impl.count(status=status)

    def delete(self, order_id: int) -> bool:
        return self._impl.delete(order_id)
