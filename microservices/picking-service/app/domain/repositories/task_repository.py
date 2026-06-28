from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import PickingTask
from ..value_objects import TaskStatusEnum


class TaskRepository(ABC):

    @abstractmethod
    def find_by_id(self, task_id: int) -> Optional[PickingTask]:
        pass

    @abstractmethod
    def find_by_order_id(self, order_id: int) -> Optional[PickingTask]:
        pass

    @abstractmethod
    def find_all(self, status: Optional[TaskStatusEnum] = None) -> List[PickingTask]:
        pass

    @abstractmethod
    def save(self, task: PickingTask) -> PickingTask:
        pass

    @abstractmethod
    def count_by_status(self, status: TaskStatusEnum) -> int:
        pass
