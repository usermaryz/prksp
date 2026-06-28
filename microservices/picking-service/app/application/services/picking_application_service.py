from __future__ import annotations

from typing import List, Optional

from ...domain.entities import PickingTask
from ...domain.repositories import TaskRepository
from ...domain.value_objects import TaskStatusEnum


class PickingApplicationService:

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create_task(
        self,
        order_id: int,
        order_number: str,
        priority: str,
        items_count: int,
    ) -> PickingTask:
        existing = self._repository.find_by_order_id(order_id)
        if existing:
            return existing

        task = PickingTask.create(
            order_id=order_id,
            order_number=order_number,
            priority=priority,
            items_count=items_count,
        )

        return self._repository.save(task)

    def get_task(self, task_id: int) -> Optional[PickingTask]:
        return self._repository.find_by_id(task_id)

    def list_tasks(self, status: Optional[str] = None) -> List[PickingTask]:
        status_enum = TaskStatusEnum(status) if status else None

        return self._repository.find_all(status=status_enum)

    def start_task(self, task_id: int, assignee: str = "Текущий пользователь") -> PickingTask:
        task = self._get_task_or_raise(task_id)
        task.start(assignee)

        return self._repository.save(task)

    def complete_task(self, task_id: int) -> PickingTask:
        task = self._get_task_or_raise(task_id)
        task.complete()

        return self._repository.save(task)

    def get_stats(self) -> dict:
        pending = self._repository.count_by_status(TaskStatusEnum.PENDING)
        in_progress = self._repository.count_by_status(TaskStatusEnum.IN_PROGRESS)
        completed = self._repository.count_by_status(TaskStatusEnum.COMPLETED)

        return {
            "pending": pending,
            "in_progress": in_progress,
            "completed_today": completed,
            "average_time_minutes": 12,
        }

    def _get_task_or_raise(self, task_id: int) -> PickingTask:
        task = self._repository.find_by_id(task_id)
        if not task:
            raise ValueError(f"Задача {task_id} не найдена")

        return task
