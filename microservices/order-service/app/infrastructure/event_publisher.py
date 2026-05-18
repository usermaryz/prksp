"""
Event Publisher
===============

Публикация Domain Events в другие микросервисы.

Варианты реализации:
1. HTTP (текущий) - синхронный вызов API
2. Message Queue - асинхронная публикация в RabbitMQ/Kafka
3. Event Store - сохранение событий для Event Sourcing

Текущая реализация использует HTTP для простоты.
В production рекомендуется Message Queue.
"""

from typing import Optional
import httpx

from ..domain.events import (
    DomainEvent,
    OrderCreatedEvent,
    OrderStatusChangedEvent,
    OrderCancelledEvent
)


class EventPublisher:
    """
    Публикатор доменных событий.
    
    Отправляет события в соответствующие микросервисы.
    """
    
    def __init__(
        self,
        picking_service_url: str = "http://localhost:8004",
        logistics_service_url: str = "http://localhost:8005",
        internal_api_key: str = "internal-service-key-2024"
    ):
        self._picking_url = picking_service_url
        self._logistics_url = logistics_service_url
        self._api_key = internal_api_key
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Публикация события.
        
        Маршрутизирует событие в соответствующий сервис.
        """
        handlers = {
            OrderCreatedEvent: self._handle_order_created,
            OrderStatusChangedEvent: self._handle_status_changed,
            OrderCancelledEvent: self._handle_order_cancelled,
        }
        
        handler = handlers.get(type(event))
        if handler:
            await handler(event)
        
        # Логирование всех событий
        print(f"[EventPublisher] Published: {event.event_name} - {event.to_dict()}")
    
    async def _handle_order_created(self, event: OrderCreatedEvent) -> None:
        """
        Обработка события OrderCreated.
        
        Создаёт задачу сборки в Picking Service.
        """
        await self._send_to_picking({
            "order_id": event.order_id,
            "order_number": event.order_number,
            "priority": "normal"
        })
    
    async def _handle_status_changed(self, event: OrderStatusChangedEvent) -> None:
        """
        Обработка события StatusChanged.
        
        При статусе PACKED - уведомляем Logistics Service.
        """
        if event.new_status == "packed":
            await self._send_to_logistics({
                "order_id": event.order_id,
                "order_number": event.order_number,
                "action": "create_shipment"
            })
    
    async def _handle_order_cancelled(self, event: OrderCancelledEvent) -> None:
        """
        Обработка события OrderCancelled.
        
        Отменяем задачу сборки в Picking Service.
        """
        await self._send_to_picking({
            "order_id": event.order_id,
            "order_number": event.order_number,
            "action": "cancel"
        })
    
    async def _send_to_picking(self, data: dict) -> Optional[dict]:
        """Отправка в Picking Service"""
        return await self._send_http(
            f"{self._picking_url}/internal/tasks",
            data
        )
    
    async def _send_to_logistics(self, data: dict) -> Optional[dict]:
        """Отправка в Logistics Service"""
        return await self._send_http(
            f"{self._logistics_url}/internal/shipments",
            data
        )
    
    async def _send_http(self, url: str, data: dict) -> Optional[dict]:
        """Отправка HTTP запроса"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=data,
                    headers={"X-Internal-Key": self._api_key}
                )
                if response.status_code in (200, 201):
                    return response.json()
                else:
                    print(f"[EventPublisher] Error: {response.status_code} - {url}")
                    return None
        except Exception as e:
            print(f"[EventPublisher] Exception: {e}")
            return None


# Singleton instance
_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Получение singleton экземпляра"""
    global _publisher
    if _publisher is None:
        _publisher = EventPublisher()
    return _publisher



