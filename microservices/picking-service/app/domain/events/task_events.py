from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from abc import ABC
import uuid


@dataclass
class DomainEvent(ABC):
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def event_name(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "occurred_at": self.occurred_at.isoformat(),
            "payload": self._payload(),
        }

    def _payload(self) -> Dict[str, Any]:
        return {}


@dataclass
class TaskCreatedEvent(DomainEvent):
    task_id: Optional[int] = None
    order_id: int = 0
    order_number: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "order_id": self.order_id,
            "order_number": self.order_number,
        }


@dataclass
class TaskStartedEvent(DomainEvent):
    task_id: Optional[int] = None
    order_id: int = 0
    assignee: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "order_id": self.order_id,
            "assignee": self.assignee,
        }


@dataclass
class TaskCompletedEvent(DomainEvent):
    task_id: Optional[int] = None
    order_id: int = 0
    order_number: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "order_id": self.order_id,
            "order_number": self.order_number,
        }


@dataclass
class TaskCancelledEvent(DomainEvent):
    task_id: Optional[int] = None
    order_id: int = 0

    def _payload(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "order_id": self.order_id,
        }
