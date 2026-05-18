"""
SQLAlchemy Order Repository
===========================

Реализация OrderRepository с использованием SQLAlchemy ORM.

Принципы:
- Реализует интерфейс из Domain Layer
- Конвертирует ORM Models <-> Domain Entities
- Изолирует SQL/ORM от бизнес-логики
"""

from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from ...domain.entities import Order, OrderItem
from ...domain.value_objects import Money, OrderStatus, OrderStatusEnum
from ...domain.repositories import OrderRepository
from .models import OrderModel, OrderItemModel


class SQLAlchemyOrderRepository(OrderRepository):
    """
    Реализация репозитория заказов на SQLAlchemy.
    
    Маппинг:
    - OrderModel -> Order (Domain Entity)
    - OrderItemModel -> OrderItem (Domain Entity)
    """
    
    def __init__(self, session: Session):
        """
        Args:
            session: SQLAlchemy Session
        """
        self._session = session
    
    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================
    
    def save(self, order: Order) -> Order:
        """
        Сохранение заказа (Create/Update).
        
        Определяет по наличию ID - создание или обновление.
        """
        if order.id is None:
            return self._create(order)
        else:
            return self._update(order)
    
    def _create(self, order: Order) -> Order:
        """Создание нового заказа"""
        model = self._to_model(order)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)
    
    def _update(self, order: Order) -> Order:
        """Обновление существующего заказа"""
        model = self._session.query(OrderModel).filter(
            OrderModel.id == order.id
        ).first()
        
        if not model:
            raise ValueError(f"Order {order.id} not found")
        
        # Обновляем поля
        model.customer_name = order.customer_name
        model.customer_phone = order.customer_phone
        model.customer_email = order.customer_email
        model.customer_address = order.customer_address
        model.status = order.status.value.value
        model.priority = order.priority
        model.notes = order.notes
        model.total = order.total.amount
        model.items_count = order.items_count
        model.updated_at = order.updated_at
        
        # Обновляем items (простой подход - удаляем и создаём заново)
        model.items.clear()
        for item in order.items:
            item_model = OrderItemModel(
                product_id=item.product_id,
                product_sku=item.product_sku,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price.amount,
                total_price=item.total_price.amount
            )
            model.items.append(item_model)
        
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)
    
    def find_by_id(self, order_id: int) -> Optional[Order]:
        """Поиск по ID"""
        model = self._session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).first()
        
        if not model:
            return None
        return self._to_entity(model)
    
    def find_by_order_number(self, order_number: str) -> Optional[Order]:
        """Поиск по номеру заказа"""
        model = self._session.query(OrderModel).filter(
            OrderModel.order_number == order_number
        ).first()
        
        if not model:
            return None
        return self._to_entity(model)
    
    def find_all(
        self,
        status: Optional[OrderStatusEnum] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Order]:
        """Получение списка с фильтрацией"""
        query = self._session.query(OrderModel)
        
        if status:
            query = query.filter(OrderModel.status == status.value)
        
        models = query.order_by(
            OrderModel.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return [self._to_entity(m) for m in models]
    
    def count(self, status: Optional[OrderStatusEnum] = None) -> int:
        """Подсчёт заказов"""
        query = self._session.query(OrderModel)
        
        if status:
            query = query.filter(OrderModel.status == status.value)
        
        return query.count()
    
    def delete(self, order_id: int) -> bool:
        """Удаление заказа"""
        model = self._session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).first()
        
        if not model:
            return False
        
        self._session.delete(model)
        self._session.commit()
        return True
    
    def find_active_orders(self) -> List[Order]:
        """Получение активных заказов"""
        active_statuses = [
            OrderStatusEnum.PENDING.value,
            OrderStatusEnum.CONFIRMED.value,
            OrderStatusEnum.PICKING.value,
            OrderStatusEnum.PACKED.value,
            OrderStatusEnum.SHIPPED.value
        ]
        
        models = self._session.query(OrderModel).filter(
            OrderModel.status.in_(active_statuses)
        ).order_by(OrderModel.created_at.desc()).all()
        
        return [self._to_entity(m) for m in models]
    
    def find_ready_for_shipping(self) -> List[Order]:
        """Заказы готовые к отправке"""
        models = self._session.query(OrderModel).filter(
            OrderModel.status == OrderStatusEnum.PACKED.value
        ).order_by(OrderModel.created_at).all()
        
        return [self._to_entity(m) for m in models]
    
    # =========================================================================
    # MAPPING: ORM Model <-> Domain Entity
    # =========================================================================
    
    def _to_entity(self, model: OrderModel) -> Order:
        """
        Конвертация ORM Model -> Domain Entity.
        
        Восстанавливает богатую доменную модель из плоских данных БД.
        """
        items = [
            OrderItem(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name or "",
                product_sku=item.product_sku or "",
                quantity=item.quantity,
                unit_price=Money(Decimal(str(item.unit_price or 0)))
            )
            for item in model.items
        ]
        
        return Order(
            id=model.id,
            order_number=model.order_number,
            customer_name=model.customer_name,
            customer_phone=model.customer_phone,
            customer_email=model.customer_email,
            customer_address=model.customer_address,
            status=OrderStatus.from_string(model.status),
            priority=model.priority or "normal",
            items=items,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, entity: Order) -> OrderModel:
        """
        Конвертация Domain Entity -> ORM Model.
        
        Подготавливает данные для сохранения в БД.
        """
        model = OrderModel(
            id=entity.id,
            order_number=entity.order_number,
            customer_name=entity.customer_name,
            customer_phone=entity.customer_phone,
            customer_email=entity.customer_email,
            customer_address=entity.customer_address,
            status=entity.status.value.value,
            priority=entity.priority,
            total=entity.total.amount,
            items_count=entity.items_count,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
        
        for item in entity.items:
            item_model = OrderItemModel(
                id=item.id,
                product_id=item.product_id,
                product_sku=item.product_sku,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price.amount,
                total_price=item.total_price.amount
            )
            model.items.append(item_model)
        
        return model



