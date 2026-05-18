"""Value Objects - Иммутабельные объекты-значения"""

from .money import Money
from .order_status import OrderStatus, OrderStatusEnum

__all__ = ['Money', 'OrderStatus', 'OrderStatusEnum']



