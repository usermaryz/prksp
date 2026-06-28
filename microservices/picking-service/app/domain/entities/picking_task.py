from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ..value_objects import TaskStatus, TaskStatusEnum
from ..events import DomainEvent, TaskCreatedEvent, TaskStartedEvent, TaskCompletedEvent, TaskCancelledEvent


@dataclass
class PickingTask:
    id: Optional[int]
    order_id: int
    order_number: str
    status: TaskStatus
    priority: str
    assigned_to: Optional[str]
    progress: int
    items_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    _events: List[DomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        order_id: int,
        order_number: str,
        priority: str,
        items_count: int,
    ) -> PickingTask:
        task = cls(
            id=None,
            order_id=order_id,
            order_number=order_number,
            status=TaskStatus.initial(),
            priority=priority,
            assigned_to=None,
            progress=0,
            items_count=items_count,
            started_at=None,
            completed_at=None,
            created_at=datetime.utcnow(),
        )
        task._add_event(TaskCreatedEvent(
            task_id=None,
            order_id=order_id,
            order_number=order_number,
        ))

        return task

    def start(self, assignee: str) -> None:
        self.status = self.status.transition_to(TaskStatusEnum.IN_PROGRESS)
        self.assigned_to = assignee
        self.started_at = datetime.utcnow()
        self._add_event(TaskStartedEvent(
            task_id=self.id,
            order_id=self.order_id,
            assignee=assignee,
        ))

    def complete(self) -> None:
        self.status = self.status.transition_to(TaskStatusEnum.COMPLETED)
        self.completed_at = datetime.utcnow()
        self.progress = 100
        self._add_event(TaskCompletedEvent(
            task_id=self.id,
            order_id=self.order_id,
            order_number=self.order_number,
        ))

    def cancel(self) -> None:
        if self.status.is_terminal():
            raise ValueError(
                f"Нельзя отменить задачу в статусе {self.status.value.value}"
            )
        self.status = self.status.transition_to(TaskStatusEnum.CANCELLED)
        self._add_event(TaskCancelledEvent(
            task_id=self.id,
            order_id=self.order_id,
        ))

    def _add_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def collect_events(self) -> List[DomainEvent]:
        events = self._events.copy()
        self._events.clear()

        return events

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PickingTask):
            return False
        if self.id and other.id:
            return self.id == other.id

        return self.order_id == other.order_id

    def __hash__(self) -> int:
        return hash(self.id or self.order_id)
