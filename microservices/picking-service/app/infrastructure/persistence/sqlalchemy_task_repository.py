from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities import PickingTask
from ...domain.repositories import TaskRepository
from ...domain.value_objects import TaskStatus, TaskStatusEnum
from .models import PickingTaskModel


class SQLAlchemyTaskRepository(TaskRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, task_id: int) -> Optional[PickingTask]:
        model = self._session.query(PickingTaskModel).filter(
            PickingTaskModel.id == task_id
        ).first()
        if not model:
            return None

        return self._to_entity(model)

    def find_by_order_id(self, order_id: int) -> Optional[PickingTask]:
        model = self._session.query(PickingTaskModel).filter(
            PickingTaskModel.order_id == order_id
        ).first()
        if not model:
            return None

        return self._to_entity(model)

    def find_all(self, status: Optional[TaskStatusEnum] = None) -> List[PickingTask]:
        query = self._session.query(PickingTaskModel)
        if status:
            query = query.filter(PickingTaskModel.status == status.value)

        models = query.order_by(PickingTaskModel.created_at.desc()).all()

        return [self._to_entity(m) for m in models]

    def save(self, task: PickingTask) -> PickingTask:
        if task.id is None:
            return self._create(task)

        return self._update(task)

    def count_by_status(self, status: TaskStatusEnum) -> int:
        return self._session.query(PickingTaskModel).filter(
            PickingTaskModel.status == status.value
        ).count()

    def _create(self, task: PickingTask) -> PickingTask:
        model = self._to_model(task)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def _update(self, task: PickingTask) -> PickingTask:
        model = self._session.query(PickingTaskModel).filter(
            PickingTaskModel.id == task.id
        ).first()
        if not model:
            raise ValueError(f"Task {task.id} not found")

        model.status = task.status.value.value
        model.priority = task.priority
        model.assigned_to = task.assigned_to
        model.progress = task.progress
        model.items_count = task.items_count
        model.started_at = task.started_at
        model.completed_at = task.completed_at

        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def _to_entity(self, model: PickingTaskModel) -> PickingTask:
        return PickingTask(
            id=model.id,
            order_id=model.order_id,
            order_number=model.order_number,
            status=TaskStatus.from_string(model.status),
            priority=model.priority or "normal",
            assigned_to=model.assigned_to,
            progress=model.progress or 0,
            items_count=model.items_count or 0,
            started_at=model.started_at,
            completed_at=model.completed_at,
            created_at=model.created_at,
        )

    def _to_model(self, task: PickingTask) -> PickingTaskModel:
        return PickingTaskModel(
            order_id=task.order_id,
            order_number=task.order_number,
            status=task.status.value.value,
            priority=task.priority,
            assigned_to=task.assigned_to,
            progress=task.progress,
            items_count=task.items_count,
            started_at=task.started_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
        )
