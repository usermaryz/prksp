from __future__ import annotations

import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


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
class UserRegisteredEvent(DomainEvent):
    username: str = ""
    email: str = ""
    role: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {"username": self.username, "email": self.email, "role": self.role}


@dataclass
class UserLoggedInEvent(DomainEvent):
    user_id: Optional[int] = None
    username: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {"user_id": self.user_id, "username": self.username}


@dataclass
class UserDeactivatedEvent(DomainEvent):
    user_id: Optional[int] = None
    username: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {"user_id": self.user_id, "username": self.username}
