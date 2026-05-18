from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas_auth import LoginResponse, LogoutIn, RefreshIn, RegisterIn, TokenOut, UserOut
from app.security import create_token, hash_password, safe_decode, verify_password
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def user_to_schema(u: User) -> UserOut:
    return UserOut(
        id=u.id,
        username=u.username,
        email=u.email,
        full_name=u.full_name,
        phone=u.phone,
        role=u.role,
        is_active=u.is_active,
        created_at=u.created_at,
        last_login_at=u.last_login_at,
    )


def issue_tokens(db: Session, user: User) -> tuple[str, str, int]:
    user.last_login_at = datetime.now(UTC)
    db.add(user)
    db.commit()

    expire_min = settings.access_token_expire_minutes
    access = create_token({"sub": str(user.id), "type": "access"}, timedelta(minutes=expire_min))
    refresh = create_token({"sub": str(user.id), "type": "refresh"}, timedelta(days=settings.refresh_token_expire_days))
    return access, refresh, expire_min * 60


@router.post("/login", response_model=LoginResponse)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)) -> LoginResponse:
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Логин или пароль указаны неверно")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Учётная запись заблокирована")

    access, refresh, secs = issue_tokens(db, user)
    return LoginResponse(user=user_to_schema(user), access_token=access, refresh_token=refresh, expires_in=secs)


@router.post("/register", response_model=UserOut)
def register(body: RegisterIn, db: Session = Depends(get_db)) -> UserOut:
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(400, detail="Такое имя пользователя уже занято")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, detail="Этот email уже зарегистрирован")

    if body.role not in {"manager", "picker", "driver"}:
        raise HTTPException(422, detail="Недопустимая роль (через регистрацию нельзя выдать admin)")

    u = User(
        username=body.username.strip(),
        email=body.email.strip(),
        hashed_password=hash_password(body.password),
        full_name=body.full_name.strip(),
        phone=body.phone,
        role=body.role,
        is_active=True,
        created_at=datetime.now(UTC),
        last_login_at=None,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return user_to_schema(u)


@router.post("/refresh", response_model=TokenOut)
def refresh_token(body: RefreshIn, db: Session = Depends(get_db)) -> TokenOut:
    data = safe_decode(body.refresh_token)
    if data is None or data.get("type") != "refresh":
        raise HTTPException(401, detail="Токен обновления недействителен")

    user = db.get(User, int(data["sub"]))
    if not user or not user.is_active:
        raise HTTPException(401, detail="Нет пользователя")

    access, ref, secs = issue_tokens(db, user)
    return TokenOut(access_token=access, refresh_token=ref, expires_in=secs)


@router.post("/logout")
def logout(_body: LogoutIn | None = None) -> dict[str, str]:
    # для учебной версии токены stateless — на клиенте просто удаляем refresh
    return {"status": "ok"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return user_to_schema(user)
