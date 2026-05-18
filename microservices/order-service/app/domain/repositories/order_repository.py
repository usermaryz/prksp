"""
Order Repository Interface
==========================

Абстрактный интерфейс репозитория для работы с заказами.

Принципы DDD:
- Repository изолирует доменный слой от инфраструктуры
- Интерфейс определён в Domain, реализация - в Infrastructure
- Работает с агрегатами целиком (не с отдельными таблицами)

Dependency Inversion Principle:
- Domain зависит от абстракции (этот интерфейс)
- Infrastructure зависит от Domain и реализует интерфейс
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Order
from ..value_objects import OrderStatusEnum


class OrderRepository(ABC):
    """
    Интерфейс репозитория заказов.
    
    Определяет контракт для persistence операций.
    Реализация находится в Infrastructure слое.
    """
    
    @abstractmethod
    def save(self, order: Order) -> Order:
        """
        Сохранить заказ (создание или обновление).
        
        Args:
            order: Агрегат заказа
            
        Returns:
            Order с присвоенным ID
        """
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[Order]:
        """
        Найти заказ по ID.
        
        Args:
            order_id: Идентификатор заказа
            
        Returns:
            Order или None если не найден
        """
        pass
    
    @abstractmethod
    def find_by_order_number(self, order_number: str) -> Optional[Order]:
        """
        Найти заказ по номеру.
        
        Args:
            order_number: Номер заказа (ORD-YYYYMMDD-XXXXX)
            
        Returns:
            Order или None
        """
        pass
    
    @abstractmethod
    def find_all(
        self,
        status: Optional[OrderStatusEnum] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Order]:
        """
        Получить список заказов с фильтрацией.
        
        Args:
            status: Фильтр по статусу
            limit: Максимальное количество
            offset: Смещение для пагинации
            
        Returns:
            Список заказов
        """
        pass
    
    @abstractmethod
    def count(self, status: Optional[OrderStatusEnum] = None) -> int:
        """
        Подсчёт заказов.
        
        Args:
            status: Фильтр по статусу
            
        Returns:
            Количество заказов
        """
        pass
    
    @abstractmethod
    def delete(self, order_id: int) -> bool:
        """
        Удалить заказ.
        
        Args:
            order_id: Идентификатор заказа
            
        Returns:
            True если удалён, False если не найден
        """
        pass
    
    @abstractmethod
    def find_active_orders(self) -> List[Order]:
        """
        Получить все активные заказы.
        
        Returns:
            Список заказов в активных статусах
        """
        pass
    
    @abstractmethod
    def find_ready_for_shipping(self) -> List[Order]:
        """
        Получить заказы, готовые к отправке (статус PACKED).
        
        Returns:
            Список упакованных заказов
        """
        pass



