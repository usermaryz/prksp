from __future__ import annotations

from typing import Optional

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository


class UserApplicationService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repository = user_repository

    def register(
        self,
        username: str,
        email: str,
        password_hash: str,
        full_name: str,
        role: str = "worker",
    ) -> User:
        user = User.create(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
        )
        saved = self._repository.save(user)
        saved.collect_events()

        return saved

    def get_user(self, user_id: int) -> Optional[User]:
        return self._repository.find_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self._repository.find_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self._repository.find_by_email(email)

    def deactivate(self, user_id: int) -> User:
        user = self._get_or_raise(user_id)
        user.deactivate()
        saved = self._repository.save(user)
        saved.collect_events()

        return saved

    def update_last_login(self, user_id: int) -> User:
        user = self._get_or_raise(user_id)
        user.update_last_login()

        return self._repository.save(user)

    def _get_or_raise(self, user_id: int) -> User:
        user = self._repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        return user
