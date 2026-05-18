"""
OrderStatus Value Object
========================

Value Object + State Machine для статусов заказа.

Инкапсулирует:
- Текущий статус
- Правила переходов между статусами
- Бизнес-логику проверки состояний

Паттерн State Machine реализован через ALLOWED_TRANSITIONS.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Set, FrozenSet


class OrderStatusEnum(str, Enum):
    """Перечисление всех возможных статусов заказа"""
    PENDING = "pending"          # Ожидает подтверждения
    CONFIRMED = "confirmed"      # Подтверждён
    PICKING = "picking"          # На сборке
    PACKED = "packed"            # Упакован
    SHIPPED = "shipped"          # Отправлен
    DELIVERED = "delivered"      # Доставлен
    CANCELLED = "cancelled"      # Отменён
    RETURNED = "returned"        # Возвращён


# =============================================================================
# STATE MACHINE - Граф допустимых переходов
# =============================================================================
ALLOWED_TRANSITIONS: dict[OrderStatusEnum, Set[OrderStatusEnum]] = {
    OrderStatusEnum.PENDING: {
        OrderStatusEnum.CONFIRMED,
        OrderStatusEnum.CANCELLED
    },
    OrderStatusEnum.CONFIRMED: {
        OrderStatusEnum.PICKING,
        OrderStatusEnum.CANCELLED
    },
    OrderStatusEnum.PICKING: {
        OrderStatusEnum.PACKED,
        OrderStatusEnum.CANCELLED
    },
    OrderStatusEnum.PACKED: {
        OrderStatusEnum.SHIPPED,
        OrderStatusEnum.CANCELLED
    },
    OrderStatusEnum.SHIPPED: {
        OrderStatusEnum.DELIVERED,
        OrderStatusEnum.RETURNED
    },
    OrderStatusEnum.DELIVERED: {
        OrderStatusEnum.RETURNED
    },
    OrderStatusEnum.CANCELLED: set(),  # Терминальное состояние
    OrderStatusEnum.RETURNED: set(),   # Терминальное состояние
}


@dataclass(frozen=True)
class OrderStatus:
    """
    Value Object для статуса заказа.
    
    Иммутабельный объект с встроенной State Machine.
    
    Примеры использования:
        >>> status = OrderStatus.initial()
        >>> status.value
        OrderStatusEnum.PENDING
        
        >>> new_status = status.transition_to(OrderStatusEnum.CONFIRMED)
        >>> new_status.value
        OrderStatusEnum.CONFIRMED
        
        >>> status.can_transition_to(OrderStatusEnum.SHIPPED)
        False  # Нельзя сразу из PENDING в SHIPPED
    """
    value: OrderStatusEnum
    
    # =========================================================================
    # STATE MACHINE METHODS
    # =========================================================================
    
    def can_transition_to(self, new_status: OrderStatusEnum) -> bool:
        """
        Проверка возможности перехода в новый статус.
        Реализация State Machine паттерна.
        """
        allowed = ALLOWED_TRANSITIONS.get(self.value, set())
        return new_status in allowed
    
    def transition_to(self, new_status: OrderStatusEnum) -> 'OrderStatus':
        """
        Переход в новый статус.
        Возвращает НОВЫЙ объект (иммутабельность).
        
        Raises:
            ValueError: Если переход недопустим
        """
        if not self.can_transition_to(new_status):
            allowed = ALLOWED_TRANSITIONS.get(self.value, set())
            allowed_str = ", ".join(s.value for s in allowed) or "нет"
            raise ValueError(
                f"Недопустимый переход: {self.value.value} -> {new_status.value}. "
                f"Допустимые переходы: {allowed_str}"
            )
        return OrderStatus(new_status)
    
    def get_allowed_transitions(self) -> FrozenSet[OrderStatusEnum]:
        """Получить все допустимые переходы из текущего состояния"""
        return frozenset(ALLOWED_TRANSITIONS.get(self.value, set()))
    
    # =========================================================================
    # BUSINESS LOGIC METHODS
    # =========================================================================
    
    def is_terminal(self) -> bool:
        """Проверка терминального состояния (нет допустимых переходов)"""
        return len(ALLOWED_TRANSITIONS.get(self.value, set())) == 0
    
    def is_active(self) -> bool:
        """Проверка активного заказа (не завершён, не отменён)"""
        return self.value not in {
            OrderStatusEnum.DELIVERED,
            OrderStatusEnum.CANCELLED,
            OrderStatusEnum.RETURNED
        }
    
    def is_cancellable(self) -> bool:
        """Можно ли отменить заказ"""
        return OrderStatusEnum.CANCELLED in ALLOWED_TRANSITIONS.get(self.value, set())
    
    def can_be_modified(self) -> bool:
        """Можно ли изменять заказ (добавлять/удалять товары)"""
        return self.value in {
            OrderStatusEnum.PENDING,
            OrderStatusEnum.CONFIRMED
        }
    
    def requires_shipping(self) -> bool:
        """Требуется ли доставка"""
        return self.value == OrderStatusEnum.PACKED
    
    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def initial(cls) -> 'OrderStatus':
        """Начальный статус для нового заказа"""
        return cls(OrderStatusEnum.PENDING)
    
    @classmethod
    def from_string(cls, status_str: str) -> 'OrderStatus':
        """Создание из строки"""
        try:
            return cls(OrderStatusEnum(status_str))
        except ValueError:
            raise ValueError(f"Неизвестный статус: {status_str}")
    
    # =========================================================================
    # COMPARISON & DISPLAY
    # =========================================================================
    
    def __str__(self) -> str:
        return self.value.value
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, OrderStatus):
            return self.value == other.value
        if isinstance(other, OrderStatusEnum):
            return self.value == other
        if isinstance(other, str):
            return self.value.value == other
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def display_name(self) -> str:
        """Человекочитаемое название статуса"""
        names = {
            OrderStatusEnum.PENDING: "Ожидает подтверждения",
            OrderStatusEnum.CONFIRMED: "Подтверждён",
            OrderStatusEnum.PICKING: "На сборке",
            OrderStatusEnum.PACKED: "Упакован",
            OrderStatusEnum.SHIPPED: "Отправлен",
            OrderStatusEnum.DELIVERED: "Доставлен",
            OrderStatusEnum.CANCELLED: "Отменён",
            OrderStatusEnum.RETURNED: "Возвращён",
        }
        return names.get(self.value, self.value.value)



