from __future__ import annotations

from ..commands import DeactivateUserCommand, RegisterUserCommand, UpdateLastLoginCommand
from ..services.user_application_service import UserApplicationService
from ...domain.entities.user import User


def handle_register_user(command: RegisterUserCommand, service: UserApplicationService) -> User:
    return service.register(
        username=command.username,
        email=command.email,
        password_hash=command.password_hash,
        full_name=command.full_name,
        role=command.role,
    )


def handle_deactivate_user(command: DeactivateUserCommand, service: UserApplicationService) -> User:
    return service.deactivate(command.user_id)


def handle_update_last_login(
    command: UpdateLastLoginCommand,
    service: UserApplicationService,
) -> User:
    return service.update_last_login(command.user_id)
