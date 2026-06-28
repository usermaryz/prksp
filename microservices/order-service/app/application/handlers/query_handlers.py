"""Query handlers — read-only operations, never mutate state."""
from __future__ import annotations

from typing import Optional

from ..queries import GetOrderQuery, ListOrdersQuery
from ..services.order_application_service import OrderApplicationService, OrderDTO


def handle_get_order(query: GetOrderQuery, service: OrderApplicationService) -> Optional[OrderDTO]:
    return service.get_order(query.order_id)


def handle_list_orders(query: ListOrdersQuery, service: OrderApplicationService) -> dict:
    return service.list_orders(status=query.status, page=query.page, limit=query.limit)
