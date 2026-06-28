from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from .models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, user: User) -> User:
        if user.id is None:
            return self._create(user)

        return self._update(user)

    def _create(self, user: User) -> User:
        model = self._to_model(user)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def _update(self, user: User) -> User:
        model = self._session.query(UserModel).filter(UserModel.id == user.id).first()
        if not model:
            raise ValueError(f"User {user.id} not found")

        model.username = user.username
        model.email = user.email
        model.password_hash = user.password_hash
        model.full_name = user.full_name
        model.phone = user.phone
        model.role = user.role
        model.is_active = user.is_active
        model.last_login_at = user.last_login_at

        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def find_by_id(self, user_id: int) -> Optional[User]:
        model = self._session.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return None

        return self._to_entity(model)

    def find_by_username(self, username: str) -> Optional[User]:
        model = self._session.query(UserModel).filter(UserModel.username == username).first()
        if not model:
            return None

        return self._to_entity(model)

    def find_by_email(self, email: str) -> Optional[User]:
        model = self._session.query(UserModel).filter(UserModel.email == email).first()
        if not model:
            return None

        return self._to_entity(model)

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            phone=model.phone,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
            last_login_at=model.last_login_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            password_hash=entity.password_hash,
            full_name=entity.full_name,
            phone=entity.phone,
            role=entity.role,
            is_active=entity.is_active,
            created_at=entity.created_at,
            last_login_at=entity.last_login_at,
        )
