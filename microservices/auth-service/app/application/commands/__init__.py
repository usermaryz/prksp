from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RegisterUserCommand:
    username: str
    email: str
    password_hash: str
    full_name: str
    phone: Optional[str] = None
    role: str = "worker"


@dataclass(frozen=True)
class DeactivateUserCommand:
    user_id: int


@dataclass(frozen=True)
class UpdateLastLoginCommand:
    user_id: int


__all__ = ["RegisterUserCommand", "DeactivateUserCommand", "UpdateLastLoginCommand"]
