from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

from jose import jwt

from ...domain.entities.user import User
from ...infrastructure.redis_client import get_redis
from ...infrastructure.persistence.sqlalchemy_refresh_token_repository import (
    RefreshTokenRecord,
    SQLAlchemyRefreshTokenRepository,
)
from .user_application_service import UserApplicationService


class TokenApplicationService:
    def __init__(
        self,
        token_repository: SQLAlchemyRefreshTokenRepository,
        user_service: UserApplicationService,
        secret_key: str,
        algorithm: str,
        access_expire_minutes: int,
        refresh_expire_days: int,
    ) -> None:
        self._tokens = token_repository
        self._users = user_service
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire_minutes = access_expire_minutes
        self._refresh_expire_days = refresh_expire_days

    def issue_refresh_token(self, user_id: int) -> str:
        user = self._users.get_user(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        jti = secrets.token_urlsafe(48)
        expires_at = datetime.utcnow() + timedelta(days=self._refresh_expire_days)
        self._tokens.create(user_id=user.id, jti=jti, expires_at=expires_at)
        return self._encode_refresh(user.id, jti, expires_at)

    def refresh_session(self, jti: str) -> Tuple[User, str, str]:
        record = self._get_valid_record(jti)
        user = self._users.get_user(record.user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        self._tokens.revoke(jti)
        get_redis().setex(
            f"revoked:{jti}",
            self._refresh_expire_days * 86400,
            "1",
        )
        access_token = self._create_access_token(user)
        refresh_token = self.issue_refresh_token(user.id)
        return user, access_token, refresh_token

    def revoke_refresh_token(self, jti: str) -> None:
        self._tokens.revoke(jti)
        get_redis().setex(
            f"revoked:{jti}",
            self._refresh_expire_days * 86400,
            "1",
        )

    def get_valid_refresh_token(self, jti: str) -> Optional[RefreshTokenRecord]:
        try:
            return self._get_valid_record(jti)
        except ValueError:
            return None

    def create_access_token(self, user: User) -> str:
        return self._create_access_token(user)

    def _get_valid_record(self, jti: str) -> RefreshTokenRecord:
        if get_redis().exists(f"revoked:{jti}"):
            raise ValueError("Refresh token revoked or expired")
        record = self._tokens.find_by_jti(jti)
        if (
            record is None
            or record.revoked_at is not None
            or record.expires_at < datetime.utcnow()
        ):
            raise ValueError("Refresh token revoked or expired")
        return record

    def _create_access_token(self, user: User) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self._access_expire_minutes)
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "type": "access",
            "exp": expire,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def _encode_refresh(self, user_id: int, jti: str, expires_at: datetime) -> str:
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "jti": jti,
            "exp": expires_at,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
