from __future__ import annotations

from typing import Optional

from ..queries import GetUserByEmailQuery, GetUserByUsernameQuery, GetUserQuery
from ..services.user_application_service import UserApplicationService
from ...domain.entities.user import User


def handle_get_user(query: GetUserQuery, service: UserApplicationService) -> Optional[User]:
    return service.get_user(query.user_id)


def handle_get_user_by_username(
    query: GetUserByUsernameQuery,
    service: UserApplicationService,
) -> Optional[User]:
    return service.get_user_by_username(query.username)


def handle_get_user_by_email(
    query: GetUserByEmailQuery,
    service: UserApplicationService,
) -> Optional[User]:
    return service.get_user_by_email(query.email)
