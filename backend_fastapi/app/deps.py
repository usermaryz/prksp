from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if creds is None or not creds.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Нет токена")
    from app.security import safe_decode

    payload = safe_decode(creds.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Неверный или просроченный токен")
    uid = payload.get("sub")
    if uid is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")
    user = db.get(User, int(uid))
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return user


def required_roles(*roles: str) -> Callable[[User], User]:
    allowed = set(roles)

    def checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль: {', '.join(sorted(allowed))}",
            )
        return user

    return checker
