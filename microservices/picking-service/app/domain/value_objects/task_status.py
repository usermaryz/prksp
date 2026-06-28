from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Set


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


ALLOWED_TRANSITIONS: dict[TaskStatusEnum, Set[TaskStatusEnum]] = {
    TaskStatusEnum.PENDING: {TaskStatusEnum.IN_PROGRESS, TaskStatusEnum.CANCELLED},
    TaskStatusEnum.IN_PROGRESS: {TaskStatusEnum.COMPLETED, TaskStatusEnum.CANCELLED},
    TaskStatusEnum.COMPLETED: set(),
    TaskStatusEnum.CANCELLED: set(),
}


@dataclass(frozen=True)
class TaskStatus:
    value: TaskStatusEnum

    def can_transition_to(self, new: TaskStatusEnum) -> bool:
        return new in ALLOWED_TRANSITIONS.get(self.value, set())

    def transition_to(self, new: TaskStatusEnum) -> TaskStatus:
        if not self.can_transition_to(new):
            allowed = ALLOWED_TRANSITIONS.get(self.value, set())
            allowed_str = ", ".join(s.value for s in allowed) or "нет"
            raise ValueError(
                f"Недопустимый переход: {self.value.value} -> {new.value}. "
                f"Допустимые переходы: {allowed_str}"
            )

        return TaskStatus(new)

    def is_terminal(self) -> bool:
        return len(ALLOWED_TRANSITIONS.get(self.value, set())) == 0

    @classmethod
    def initial(cls) -> TaskStatus:
        return cls(TaskStatusEnum.PENDING)

    @classmethod
    def from_string(cls, value: str) -> TaskStatus:
        try:
            return cls(TaskStatusEnum(value))
        except ValueError:
            raise ValueError(f"Неизвестный статус задачи: {value}")

    def __str__(self) -> str:
        return self.value.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TaskStatus):
            return self.value == other.value
        if isinstance(other, TaskStatusEnum):
            return self.value == other
        if isinstance(other, str):
            return self.value.value == other

        return False

    def __hash__(self) -> int:
        return hash(self.value)
