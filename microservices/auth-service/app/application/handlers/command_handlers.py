from __future__ import annotations

from ..commands import (
    DeactivateUserCommand,
    IssueRefreshTokenCommand,
    RefreshSessionCommand,
    RegisterUserCommand,
    RevokeRefreshTokenCommand,
    UpdateLastLoginCommand,
)
from ..services.token_application_service import TokenApplicationService
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


def handle_issue_refresh_token(
    command: IssueRefreshTokenCommand,
    service: TokenApplicationService,
) -> str:
    return service.issue_refresh_token(command.user_id)


def handle_refresh_session(
    command: RefreshSessionCommand,
    service: TokenApplicationService,
) -> tuple[User, str, str]:
    return service.refresh_session(command.jti)


def handle_revoke_refresh_token(
    command: RevokeRefreshTokenCommand,
    service: TokenApplicationService,
) -> None:
    service.revoke_refresh_token(command.jti)
