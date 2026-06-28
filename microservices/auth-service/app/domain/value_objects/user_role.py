from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    PICKER = "picker"
    DRIVER = "driver"
    WORKER = "worker"


@dataclass(frozen=True)
class UserRole:
    value: UserRoleEnum

    @classmethod
    def from_string(cls, role: str) -> "UserRole":
        try:
            return cls(UserRoleEnum(role))
        except ValueError:
            raise ValueError(f"Unknown role: {role}")

    def display_name(self) -> str:
        names = {
            UserRoleEnum.ADMIN: "Администратор",
            UserRoleEnum.MANAGER: "Менеджер",
            UserRoleEnum.PICKER: "Сборщик",
            UserRoleEnum.DRIVER: "Водитель",
            UserRoleEnum.WORKER: "Работник",
        }

        return names.get(self.value, self.value.value)

    def can_manage_users(self) -> bool:
        return self.value in {UserRoleEnum.ADMIN, UserRoleEnum.MANAGER}

    def __str__(self) -> str:
        return self.value.value
