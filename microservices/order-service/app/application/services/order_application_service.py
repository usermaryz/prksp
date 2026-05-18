"""
Order Application Service
=========================

Application Service для оркестрации use cases заказов.

Ответственности:
- Оркестрация Domain объектов
- Управление транзакциями
- Публикация Domain Events
- Преобразование DTO <-> Domain

НЕ содержит бизнес-логику (она в Domain Layer).
"""

from typing import List, Optional
from dataclasses import dataclass

from ...domain.entities import Order, OrderItem
from ...domain.value_objects import Money, OrderStatus, OrderStatusEnum
from ...domain.repositories import OrderRepository
from ...domain.events import DomainEvent


# =============================================================================
# DTOs (Data Transfer Objects)
# =============================================================================

@dataclass
class CreateOrderDTO:
    """DTO для создания заказа"""
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    priority: str = "normal"
    notes: Optional[str] = None


@dataclass
class AddItemDTO:
    """DTO для добавления позиции"""
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_price: float


@dataclass
class OrderDTO:
    """DTO для возврата данных заказа"""
    id: int
    order_number: str
    customer_name: str
    customer_phone: str
    customer_email: Optional[str]
    customer_address: Optional[str]
    status: str
    status_display: str
    priority: str
    total: float
    total_formatted: str
    items_count: int
    items: List[dict]
    created_at: str
    updated_at: str
    
    @classmethod
    def from_entity(cls, order: Order) -> 'OrderDTO':
        """Преобразование Entity -> DTO"""
        return cls(
            id=order.id,
            order_number=order.order_number,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_email=order.customer_email,
            customer_address=order.customer_address,
            status=order.status.value.value,
            status_display=order.status.display_name(),
            priority=order.priority,
            total=float(order.total.amount),
            total_formatted=order.total.format(),
            items_count=order.items_count,
            items=[
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "product_sku": item.product_sku,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price.amount),
                    "total_price": float(item.total_price.amount)
                }
                for item in order.items
            ],
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat()
        )


# =============================================================================
# APPLICATION SERVICE
# =============================================================================

class OrderApplicationService:
    """
    Application Service для управления заказами.
    
    Координирует работу Domain объектов и Repository.
    """
    
    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: Optional[callable] = None
    ):
        """
        Args:
            order_repository: Репозиторий заказов
            event_publisher: Функция публикации событий (опционально)
        """
        self._repository = order_repository
        self._event_publisher = event_publisher
    
    # =========================================================================
    # COMMANDS (изменение состояния)
    # =========================================================================
    
    def create_order(self, dto: CreateOrderDTO) -> OrderDTO:
        """
        Use Case: Создание заказа.
        
        1. Создаёт Domain Entity через фабричный метод
        2. Сохраняет через Repository
        3. Публикует Domain Events
        4. Возвращает DTO
        """
        # Создаём агрегат через фабричный метод
        order = Order.create(
            customer_name=dto.customer_name,
            customer_phone=dto.customer_phone,
            customer_email=dto.customer_email,
            customer_address=dto.customer_address,
            priority=dto.priority,
            notes=dto.notes
        )
        
        # Сохраняем (репозиторий присвоит ID)
        saved_order = self._repository.save(order)
        
        # Публикуем события
        self._publish_events(saved_order.collect_events())
        
        return OrderDTO.from_entity(saved_order)
    
    def add_item(self, order_id: int, dto: AddItemDTO) -> OrderDTO:
        """
        Use Case: Добавление позиции в заказ.
        
        Делегирует бизнес-логику Entity.
        """
        order = self._get_order_or_raise(order_id)
        
        order.add_item(
            product_id=dto.product_id,
            product_name=dto.product_name,
            product_sku=dto.product_sku,
            quantity=dto.quantity,
            unit_price=Money.from_float(dto.unit_price)
        )
        
        saved_order = self._repository.save(order)
        self._publish_events(saved_order.collect_events())
        
        return OrderDTO.from_entity(saved_order)
    
    def remove_item(self, order_id: int, product_id: int) -> OrderDTO:
        """Use Case: Удаление позиции из заказа"""
        order = self._get_order_or_raise(order_id)
        order.remove_item(product_id)
        
        saved_order = self._repository.save(order)
        return OrderDTO.from_entity(saved_order)
    
    def change_status(self, order_id: int, new_status: str) -> OrderDTO:
        """
        Use Case: Изменение статуса заказа.
        
        Валидация переходов делегируется Value Object OrderStatus.
        """
        order = self._get_order_or_raise(order_id)
        
        status_enum = OrderStatusEnum(new_status)
        order.change_status(status_enum)
        
        saved_order = self._repository.save(order)
        self._publish_events(saved_order.collect_events())
        
        return OrderDTO.from_entity(saved_order)
    
    def confirm_order(self, order_id: int) -> OrderDTO:
        """Use Case: Подтверждение заказа"""
        order = self._get_order_or_raise(order_id)
        order.confirm()
        
        saved_order = self._repository.save(order)
        self._publish_events(saved_order.collect_events())
        
        return OrderDTO.from_entity(saved_order)
    
    def cancel_order(self, order_id: int, reason: Optional[str] = None) -> OrderDTO:
        """Use Case: Отмена заказа"""
        order = self._get_order_or_raise(order_id)
        order.cancel(reason)
        
        saved_order = self._repository.save(order)
        self._publish_events(saved_order.collect_events())
        
        return OrderDTO.from_entity(saved_order)
    
    def delete_order(self, order_id: int) -> bool:
        """Use Case: Удаление заказа"""
        return self._repository.delete(order_id)
    
    # =========================================================================
    # QUERIES (чтение)
    # =========================================================================
    
    def get_order(self, order_id: int) -> Optional[OrderDTO]:
        """Query: Получение заказа по ID"""
        order = self._repository.find_by_id(order_id)
        if not order:
            return None
        return OrderDTO.from_entity(order)
    
    def get_order_by_number(self, order_number: str) -> Optional[OrderDTO]:
        """Query: Получение заказа по номеру"""
        order = self._repository.find_by_order_number(order_number)
        if not order:
            return None
        return OrderDTO.from_entity(order)
    
    def list_orders(
        self,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> dict:
        """
        Query: Список заказов с пагинацией.
        
        Returns:
            dict с data (список OrderDTO) и meta (пагинация)
        """
        status_enum = OrderStatusEnum(status) if status else None
        offset = (page - 1) * limit
        
        orders = self._repository.find_all(
            status=status_enum,
            limit=limit,
            offset=offset
        )
        total = self._repository.count(status=status_enum)
        
        return {
            "data": [OrderDTO.from_entity(o) for o in orders],
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    
    def get_orders_ready_for_shipping(self) -> List[OrderDTO]:
        """Query: Заказы готовые к отправке"""
        orders = self._repository.find_ready_for_shipping()
        return [OrderDTO.from_entity(o) for o in orders]
    
    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================
    
    def _get_order_or_raise(self, order_id: int) -> Order:
        """Получить заказ или выбросить исключение"""
        order = self._repository.find_by_id(order_id)
        if not order:
            raise ValueError(f"Заказ {order_id} не найден")
        return order
    
    def _publish_events(self, events: List[DomainEvent]) -> None:
        """Публикация доменных событий"""
        if self._event_publisher:
            for event in events:
                self._event_publisher(event)



