from __future__ import annotations

from typing import List, Optional

from ...domain.entities import PickingTask
from ..queries import GetTaskQuery, ListTasksQuery, GetStatsQuery
from ..services import PickingApplicationService


def handle_get_task(query: GetTaskQuery, service: PickingApplicationService) -> Optional[PickingTask]:
    return service.get_task(query.task_id)


def handle_list_tasks(query: ListTasksQuery, service: PickingApplicationService) -> List[PickingTask]:
    return service.list_tasks(status=query.status)


def handle_get_stats(query: GetStatsQuery, service: PickingApplicationService) -> dict:
    return service.get_stats()
