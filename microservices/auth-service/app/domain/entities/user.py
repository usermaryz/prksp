from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ..events.user_events import DomainEvent, UserDeactivatedEvent, UserRegisteredEvent


@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    password_hash: str
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime]
    last_login_at: Optional[datetime]

    _events: List[DomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        password_hash: str,
        full_name: str,
        role: str = "worker",
    ) -> "User":
        user = cls(
            id=None,
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone=None,
            role=role,
            is_active=True,
            created_at=datetime.utcnow(),
            last_login_at=None,
        )
        user._add_event(UserRegisteredEvent(username=username, email=email, role=role))

        return user

    def deactivate(self) -> None:
        self.is_active = False
        self._add_event(UserDeactivatedEvent(user_id=self.id, username=self.username))

    def update_last_login(self) -> None:
        self.last_login_at = datetime.utcnow()

    def change_role(self, role: str) -> None:
        self.role = role

    def _add_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def collect_events(self) -> List[DomainEvent]:
        events = self._events.copy()
        self._events.clear()

        return events
