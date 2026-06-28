from __future__ import annotations

from ...domain.entities import PickingTask
from ..commands import CreateTaskCommand, StartTaskCommand, CompleteTaskCommand
from ..services import PickingApplicationService


def handle_create_task(command: CreateTaskCommand, service: PickingApplicationService) -> PickingTask:
    return service.create_task(
        order_id=command.order_id,
        order_number=command.order_number,
        priority=command.priority,
        items_count=command.items_count,
    )


def handle_start_task(command: StartTaskCommand, service: PickingApplicationService) -> PickingTask:
    return service.start_task(command.task_id, assignee=command.assignee)


def handle_complete_task(command: CompleteTaskCommand, service: PickingApplicationService) -> PickingTask:
    return service.complete_task(command.task_id)
