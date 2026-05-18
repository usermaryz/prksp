"""
Domain Events для Order Aggregate
==================================

События генерируются сущностями при значимых изменениях.
Используются для:
- Уведомления других микросервисов
- Audit logging
- Eventual consistency между сервисами

Паттерн: Event Sourcing ready (события можно сохранять)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any, Dict
from abc import ABC
import uuid


@dataclass
class DomainEvent(ABC):
    """
    Базовый класс для всех доменных событий.
    
    Свойства:
    - Уникальный идентификатор события
    - Время возникновения
    - Имя события
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def event_name(self) -> str:
        """Имя события (имя класса)"""
        return self.__class__.__name__
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь для отправки"""
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "occurred_at": self.occurred_at.isoformat(),
            "payload": self._payload()
        }
    
    def _payload(self) -> Dict[str, Any]:
        """Переопределить в наследниках для специфичных данных"""
        return {}


@dataclass
class OrderCreatedEvent(DomainEvent):
    """
    Событие: Заказ создан.
    
    Публикуется при создании нового заказа.
    Подписчики:
    - Picking Service (создание задачи сборки)
    - Notification Service (уведомление клиента)
    """
    order_id: Optional[int] = None
    order_number: str = ""
    customer_name: str = ""
    
    def _payload(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "order_number": self.order_number,
            "customer_name": self.customer_name
        }


@dataclass
class OrderStatusChangedEvent(DomainEvent):
    """
    Событие: Статус заказа изменён.
    
    Публикуется при любом изменении статуса.
    Подписчики:
    - Logistics Service (при статусе PACKED -> создание отправки)
    - Notification Service (уведомление клиента)
    - Analytics Service (метрики)
    """
    order_id: Optional[int] = None
    order_number: str = ""
    old_status: str = ""
    new_status: str = ""
    
    def _payload(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "order_number": self.order_number,
            "old_status": self.old_status,
            "new_status": self.new_status
        }


@dataclass
class OrderCancelledEvent(DomainEvent):
    """
    Событие: Заказ отменён.
    
    Подписчики:
    - Inventory Service (освобождение резерва)
    - Picking Service (отмена задачи сборки)
    - Notification Service
    """
    order_id: Optional[int] = None
    order_number: str = ""
    reason: Optional[str] = None
    
    def _payload(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "order_number": self.order_number,
            "reason": self.reason
        }


@dataclass  
class OrderItemAddedEvent(DomainEvent):
    """Событие: Товар добавлен в заказ"""
    order_id: Optional[int] = None
    order_number: str = ""
    product_id: int = 0
    product_name: str = ""
    quantity: int = 0
    
    def _payload(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "order_number": self.order_number,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity
        }



