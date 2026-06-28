from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateTaskCommand:
    order_id: int
    order_number: str
    priority: str
    items_count: int


@dataclass(frozen=True)
class StartTaskCommand:
    task_id: int
    assignee: str = "Текущий пользователь"


@dataclass(frozen=True)
class CompleteTaskCommand:
    task_id: int


__all__ = ["CreateTaskCommand", "StartTaskCommand", "CompleteTaskCommand"]
