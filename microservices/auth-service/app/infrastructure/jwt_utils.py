from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .persistence.models import RefreshTokenModel


def create_access_token(
    user,
    secret_key: str,
    algorithm: str,
    expire_minutes: int,
) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "type": "access",
        "exp": expire,
    }

    return jwt.encode(payload, secret_key, algorithm=algorithm)


def create_refresh_token_record(
    db: Session,
    user,
    secret_key: str,
    algorithm: str,
    expire_days: int,
) -> str:
    jti = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(days=expire_days)
    db.add(RefreshTokenModel(user_id=user.id, token=jti, expires_at=expires_at))
    db.flush()
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "jti": jti,
        "exp": expires_at,
    }

    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_token(token: str, secret_key: str, algorithm: str) -> Optional[dict]:
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        return None
