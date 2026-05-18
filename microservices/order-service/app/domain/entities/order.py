"""
Order Aggregate Root
====================

Агрегат заказа - центральная сущность Order Service.

Принципы DDD:
- Aggregate Root управляет дочерними сущностями (OrderItem)
- Инкапсуляция бизнес-правил
- Генерация Domain Events при изменениях
- Защита инвариантов

Order является Aggregate Root, так как:
1. Имеет уникальную идентичность (id, order_number)
2. Управляет жизненным циклом OrderItem
3. Гарантирует целостность данных
4. Является точкой входа для всех операций с заказом
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import random

from ..value_objects import Money, OrderStatus, OrderStatusEnum
from ..events import DomainEvent, OrderCreatedEvent, OrderStatusChangedEvent


@dataclass
class OrderItem:
    """
    Entity - Позиция заказа.
    
    Дочерняя сущность агрегата Order.
    Имеет идентичность только в контексте родительского заказа.
    """
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_price: Money
    id: Optional[int] = None
    
    def __post_init__(self):
        """Валидация при создании"""
        if self.quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        if self.unit_price.amount < 0:
            raise ValueError("Цена не может быть отрицательной")
    
    @property
    def total_price(self) -> Money:
        """Вычисляемое свойство - общая стоимость позиции"""
        return self.unit_price * self.quantity
    
    def update_quantity(self, new_quantity: int) -> None:
        """
        Изменение количества.
        Бизнес-правило: количество > 0
        """
        if new_quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        self.quantity = new_quantity
    
    def __eq__(self, other: object) -> bool:
        """Сравнение по product_id в контексте заказа"""
        if not isinstance(other, OrderItem):
            return False
        return self.product_id == other.product_id


@dataclass
class Order:
    """
    Aggregate Root - Заказ.
    
    Главная сущность, управляющая всем агрегатом.
    Все изменения проходят через методы Order.
    
    Примеры использования:
        >>> order = Order.create(
        ...     customer_name="Иван Иванов",
        ...     customer_phone="+7 999 123-45-67"
        ... )
        >>> order.add_item(
        ...     product_id=1,
        ...     product_name="iPhone 15",
        ...     product_sku="IPH-15-128",
        ...     quantity=2,
        ...     unit_price=Money.from_float(89990)
        ... )
        >>> order.confirm()
        >>> print(order.total.format())
        179,980.00 RUB
    """
    
    # Идентификация
    id: Optional[int]
    order_number: str
    
    # Данные клиента
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    
    # Состояние (Value Object)
    status: OrderStatus = field(default_factory=OrderStatus.initial)
    priority: str = "normal"
    
    # Дочерние сущности
    items: List[OrderItem] = field(default_factory=list)
    
    # Метаданные
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Domain Events (не сохраняются в БД)
    _domain_events: List[DomainEvent] = field(default_factory=list, repr=False)
    
    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def create(
        cls,
        customer_name: str,
        customer_phone: str,
        customer_email: Optional[str] = None,
        customer_address: Optional[str] = None,
        priority: str = "normal",
        notes: Optional[str] = None
    ) -> 'Order':
        """
        Фабричный метод создания заказа.
        
        Генерирует уникальный номер заказа и событие OrderCreated.
        """
        order_number = cls._generate_order_number()
        
        order = cls(
            id=None,
            order_number=order_number,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            customer_address=customer_address,
            priority=priority,
            notes=notes
        )
        
        # Генерируем доменное событие
        order._add_event(OrderCreatedEvent(
            order_id=None,  # ID появится после сохранения
            order_number=order_number,
            customer_name=customer_name
        ))
        
        return order
    
    @staticmethod
    def _generate_order_number() -> str:
        """Генерация уникального номера заказа"""
        date_part = datetime.now().strftime('%Y%m%d')
        random_part = random.randint(10000, 99999)
        return f"ORD-{date_part}-{random_part}"
    
    # =========================================================================
    # ITEM MANAGEMENT (Aggregate Root responsibility)
    # =========================================================================
    
    def add_item(
        self,
        product_id: int,
        product_name: str,
        product_sku: str,
        quantity: int,
        unit_price: Money
    ) -> OrderItem:
        """
        Добавление позиции в заказ.
        
        Бизнес-правила:
        - Можно добавлять только в статусах PENDING/CONFIRMED
        - Если товар уже есть - увеличиваем количество
        
        Raises:
            ValueError: Если заказ нельзя изменять
        """
        if not self.status.can_be_modified():
            raise ValueError(
                f"Нельзя изменять заказ в статусе {self.status.display_name()}"
            )
        
        # Проверяем, есть ли уже такой товар
        existing_item = self._find_item_by_product(product_id)
        if existing_item:
            existing_item.update_quantity(existing_item.quantity + quantity)
            self._touch()
            return existing_item
        
        # Создаём новую позицию
        item = OrderItem(
            product_id=product_id,
            product_name=product_name,
            product_sku=product_sku,
            quantity=quantity,
            unit_price=unit_price
        )
        self.items.append(item)
        self._touch()
        
        return item
    
    def remove_item(self, product_id: int) -> None:
        """
        Удаление позиции из заказа.
        
        Raises:
            ValueError: Если заказ нельзя изменять или товар не найден
        """
        if not self.status.can_be_modified():
            raise ValueError(
                f"Нельзя изменять заказ в статусе {self.status.display_name()}"
            )
        
        item = self._find_item_by_product(product_id)
        if not item:
            raise ValueError(f"Товар {product_id} не найден в заказе")
        
        self.items.remove(item)
        self._touch()
    
    def update_item_quantity(self, product_id: int, quantity: int) -> None:
        """Изменение количества товара в позиции"""
        if not self.status.can_be_modified():
            raise ValueError(
                f"Нельзя изменять заказ в статусе {self.status.display_name()}"
            )
        
        item = self._find_item_by_product(product_id)
        if not item:
            raise ValueError(f"Товар {product_id} не найден в заказе")
        
        item.update_quantity(quantity)
        self._touch()
    
    def _find_item_by_product(self, product_id: int) -> Optional[OrderItem]:
        """Поиск позиции по ID товара"""
        return next((item for item in self.items if item.product_id == product_id), None)
    
    # =========================================================================
    # STATUS TRANSITIONS (State Machine через Value Object)
    # =========================================================================
    
    def change_status(self, new_status: OrderStatusEnum) -> None:
        """
        Изменение статуса заказа.
        
        Делегирует валидацию Value Object OrderStatus.
        Генерирует событие OrderStatusChanged.
        """
        old_status = self.status
        self.status = self.status.transition_to(new_status)
        self._touch()
        
        self._add_event(OrderStatusChangedEvent(
            order_id=self.id,
            order_number=self.order_number,
            old_status=old_status.value.value,
            new_status=new_status.value
        ))
    
    def confirm(self) -> None:
        """Подтвердить заказ"""
        self.change_status(OrderStatusEnum.CONFIRMED)
    
    def start_picking(self) -> None:
        """Начать сборку"""
        self.change_status(OrderStatusEnum.PICKING)
    
    def pack(self) -> None:
        """Упаковать заказ"""
        self.change_status(OrderStatusEnum.PACKED)
    
    def ship(self) -> None:
        """Отправить заказ"""
        self.change_status(OrderStatusEnum.SHIPPED)
    
    def deliver(self) -> None:
        """Отметить как доставленный"""
        self.change_status(OrderStatusEnum.DELIVERED)
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """
        Отменить заказ.
        
        Args:
            reason: Причина отмены (опционально)
        """
        if not self.status.is_cancellable():
            raise ValueError(
                f"Нельзя отменить заказ в статусе {self.status.display_name()}"
            )
        
        if reason:
            self.notes = f"{self.notes or ''}\n[Причина отмены] {reason}".strip()
        
        self.change_status(OrderStatusEnum.CANCELLED)
    
    # =========================================================================
    # COMPUTED PROPERTIES
    # =========================================================================
    
    @property
    def total(self) -> Money:
        """Общая стоимость заказа (вычисляемое свойство)"""
        if not self.items:
            return Money.zero()
        return sum((item.total_price for item in self.items), Money.zero())
    
    @property
    def items_count(self) -> int:
        """Количество позиций в заказе"""
        return len(self.items)
    
    @property
    def total_quantity(self) -> int:
        """Общее количество товаров"""
        return sum(item.quantity for item in self.items)
    
    @property
    def is_empty(self) -> bool:
        """Пустой ли заказ"""
        return len(self.items) == 0
    
    # =========================================================================
    # DOMAIN EVENTS
    # =========================================================================
    
    def _add_event(self, event: DomainEvent) -> None:
        """Добавление доменного события"""
        self._domain_events.append(event)
    
    def collect_events(self) -> List[DomainEvent]:
        """
        Получение и очистка списка событий.
        Вызывается после сохранения агрегата.
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    # =========================================================================
    # INTERNAL
    # =========================================================================
    
    def _touch(self) -> None:
        """Обновление времени изменения"""
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Сравнение по идентичности (ID или номеру заказа)"""
        if not isinstance(other, Order):
            return False
        if self.id and other.id:
            return self.id == other.id
        return self.order_number == other.order_number
    
    def __hash__(self) -> int:
        return hash(self.order_number)



