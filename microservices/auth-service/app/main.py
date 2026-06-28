"""
Auth Service — DDD + CQRS + Redis architecture.

Layers:
  domain/         — User (Aggregate Root), UserRole (Value Object),
                    Domain Events
  application/    — Commands, Queries, Handlers, CommandBus, QueryBus,
                    UserApplicationService
  infrastructure/ — SQLAlchemyUserRepository, JwtUtils, RedisClient
  main.py         — FastAPI endpoints (thin adapter)
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .application.bus import CommandBus, QueryBus
from .application.commands import (
    DeactivateUserCommand,
    RegisterUserCommand,
    UpdateLastLoginCommand,
)
from .application.handlers.command_handlers import (
    handle_deactivate_user,
    handle_register_user,
    handle_update_last_login,
)
from .application.handlers.query_handlers import (
    handle_get_user,
    handle_get_user_by_email,
    handle_get_user_by_username,
)
from .application.queries import (
    GetUserByEmailQuery,
    GetUserByUsernameQuery,
    GetUserQuery,
)
from .application.services import UserApplicationService
from .infrastructure.jwt_utils import (
    create_access_token,
    create_refresh_token_record,
    decode_token,
)
from .infrastructure.persistence import Base, SQLAlchemyUserRepository
from .infrastructure.persistence.models import RefreshTokenModel
from .infrastructure.redis_client import get_redis, verify_redis_connection
from .wms_config import require_env


# =============================================================================
# CONFIG
# =============================================================================
SERVICE_NAME = "auth-service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "auth.db")


def _sync_db_url(raw: str, fallback: str) -> str:
    if not raw:
        return fallback
    raw = raw.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if raw.startswith("postgres://"):
        raw = "postgresql+psycopg2://" + raw[len("postgres://"):]

    return raw


DATABASE_URL = _sync_db_url(
    os.getenv("DATABASE_URL", "").strip(),
    f"sqlite:///{DATABASE_PATH}",
)

_secret = os.getenv("SECRET_KEY", "")
if not _secret:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Generate one with: openssl rand -hex 32"
    )
SECRET_KEY = _secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
INTERNAL_API_KEY = require_env(
    "INTERNAL_API_KEY",
    "Generate with: openssl rand -hex 32",
)
ENABLE_DEMO_SEED = (
    os.getenv("ENABLE_DEMO_SEED", "true").lower() in ("1", "true", "yes")
)

_connect_args = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    expires_in: int


class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


# =============================================================================
# HELPERS
# =============================================================================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def _user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
    )


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_service(db: Session = Depends(get_db)) -> UserApplicationService:
    repository = SQLAlchemyUserRepository(db)

    return UserApplicationService(user_repository=repository)


def get_command_bus(
    service: UserApplicationService = Depends(get_user_service),
) -> CommandBus:
    bus = CommandBus()
    bus.register(
        RegisterUserCommand,
        lambda cmd: handle_register_user(cmd, service),
    )
    bus.register(
        DeactivateUserCommand,
        lambda cmd: handle_deactivate_user(cmd, service),
    )
    bus.register(
        UpdateLastLoginCommand,
        lambda cmd: handle_update_last_login(cmd, service),
    )

    return bus


def get_query_bus(
    service: UserApplicationService = Depends(get_user_service),
) -> QueryBus:
    bus = QueryBus()
    bus.register(GetUserQuery, lambda q: handle_get_user(q, service))
    bus.register(
        GetUserByUsernameQuery,
        lambda q: handle_get_user_by_username(q, service),
    )
    bus.register(
        GetUserByEmailQuery,
        lambda q: handle_get_user_by_email(q, service),
    )

    return bus


def verify_internal_key(x_internal_key: str = Header(None)):
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal API key")

    return True


# =============================================================================
# INIT / SEED
# =============================================================================
def init_database():
    Base.metadata.create_all(bind=engine)
    if not ENABLE_DEMO_SEED:
        return
    db = SessionLocal()
    try:
        service = UserApplicationService(SQLAlchemyUserRepository(db))
        demo_users = [
            ("admin", "admin@wms.local", "admin", "Администратор", "admin"),
            ("manager", "manager@wms.local", "manager", "Менеджер", "manager"),
            ("picker", "picker@wms.local", "picker", "Сборщик", "picker"),
            ("driver", "driver@wms.local", "driver", "Водитель", "driver"),
        ]
        for username, email, password, full_name, role in demo_users:
            if not service.get_user_by_username(username):
                service.register(
                    username=username,
                    email=email,
                    password_hash=hash_password(password),
                    full_name=full_name,
                    role=role,
                )
        print(
            f"[{SERVICE_NAME}] Demo users seeded "
            "(set ENABLE_DEMO_SEED=false to disable)"
        )
    finally:
        db.close()


# =============================================================================
# APP
# =============================================================================
@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    verify_redis_connection()
    print(
        f"[{SERVICE_NAME}] Starting on port {SERVICE_PORT} (DDD+CQRS+Redis)..."
    )
    yield
    print(f"[{SERVICE_NAME}] Shutting down...")


app = FastAPI(title="Auth Service", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ENDPOINTS
# =============================================================================
@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME, "port": SERVICE_PORT}


@app.post("/auth/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    query_bus: QueryBus = Depends(get_query_bus),
    command_bus: CommandBus = Depends(get_command_bus),
):
    user = query_bus.ask(GetUserByUsernameQuery(username=form_data.username))
    if not user:
        user = query_bus.ask(GetUserByEmailQuery(email=form_data.username))
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401, detail="Неверный логин или пароль",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=403, detail="Пользователь заблокирован",
        )

    command_bus.dispatch(UpdateLastLoginCommand(user_id=user.id))
    user = query_bus.ask(GetUserQuery(user_id=user.id))

    access_token = create_access_token(
        user, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token = create_refresh_token_record(
        db, user, SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS,
    )
    db.commit()

    return LoginResponse(
        user=_user_response(user),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.post("/auth/refresh", response_model=LoginResponse)
def refresh_tokens(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token, SECRET_KEY, ALGORITHM)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Неверный refresh-токен")

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=401, detail="Неверный refresh-токен")

    r = get_redis()
    if r.exists(f"revoked:{jti}"):
        raise HTTPException(
            status_code=401, detail="Refresh-токен отозван или просрочен",
        )

    row = (
        db.query(RefreshTokenModel)
        .filter(RefreshTokenModel.token == jti)
        .first()
    )
    if not row or row.revoked_at is not None or row.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=401, detail="Refresh-токен отозван или просрочен",
        )

    service = UserApplicationService(SQLAlchemyUserRepository(db))
    user = service.get_user(row.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    row.revoked_at = datetime.utcnow()
    r.setex(f"revoked:{jti}", REFRESH_TOKEN_EXPIRE_DAYS * 86400, "1")

    access_token = create_access_token(
        user, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    new_refresh = create_refresh_token_record(
        db, user, SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS,
    )
    db.commit()

    return LoginResponse(
        user=_user_response(user),
        access_token=access_token,
        refresh_token=new_refresh,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.post("/auth/logout")
def logout(body: LogoutRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token, SECRET_KEY, ALGORITHM)
    if payload and payload.get("type") == "refresh":
        jti = payload.get("jti")
        if jti:
            row = (
                db.query(RefreshTokenModel)
                .filter(RefreshTokenModel.token == jti)
                .first()
            )
            if row and row.revoked_at is None:
                row.revoked_at = datetime.utcnow()
                db.commit()
            get_redis().setex(f"revoked:{jti}", REFRESH_TOKEN_EXPIRE_DAYS * 86400, "1")

    return {"status": "ok"}


@app.post("/auth/register", response_model=UserResponse)
def register(
    data: RegisterRequest,
    command_bus: CommandBus = Depends(get_command_bus),
    query_bus: QueryBus = Depends(get_query_bus),
):
    existing = query_bus.ask(GetUserByUsernameQuery(username=data.username))
    if not existing:
        existing = query_bus.ask(GetUserByEmailQuery(email=data.email))
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    user = command_bus.dispatch(
        RegisterUserCommand(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
        )
    )

    return _user_response(user)


@app.get("/auth/me", response_model=UserResponse)
def get_me(
    authorization: str = Header(None),
    query_bus: QueryBus = Depends(get_query_bus),
):
    user_id = _extract_user_id_from_bearer(authorization, token_type="access")
    user = query_bus.ask(GetUserQuery(user_id=user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return _user_response(user)


@app.post("/internal/validate", response_model=TokenValidationResponse)
def validate_token(
    authorization: str = Header(None),
    _: bool = Depends(verify_internal_key),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        return TokenValidationResponse(valid=False)
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token, SECRET_KEY, ALGORITHM)
    if not payload or payload.get("type") != "access":
        return TokenValidationResponse(valid=False)

    user_id = int(payload.get("sub", 0))

    r = get_redis()
    cached_role = r.get(f"user_role:{user_id}")
    if cached_role:
        role = (
            cached_role.decode()
            if isinstance(cached_role, bytes)
            else cached_role
        )

        return TokenValidationResponse(
            valid=True,
            user_id=user_id,
            username=payload.get("username"),
            role=role,
        )

    service = UserApplicationService(SQLAlchemyUserRepository(db))
    user = service.get_user(user_id)
    if not user or not user.is_active:
        return TokenValidationResponse(valid=False)

    r.setex(f"user_role:{user_id}", 60, user.role)

    return TokenValidationResponse(
        valid=True,
        user_id=user.id,
        username=user.username,
        role=user.role,
    )


@app.get("/internal/users/{user_id}", response_model=UserResponse)
def get_user_internal(
    user_id: int,
    _: bool = Depends(verify_internal_key),
    query_bus: QueryBus = Depends(get_query_bus),
):
    user = query_bus.ask(GetUserQuery(user_id=user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return _user_response(user)


# =============================================================================
# PRIVATE HELPERS
# =============================================================================
def _extract_user_id_from_bearer(
    authorization: Optional[str],
    token_type: str = "access",
) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token, SECRET_KEY, ALGORITHM)
    if not payload or payload.get("type") != token_type:
        raise HTTPException(status_code=401, detail="Invalid token")

    return int(payload.get("sub", 0))


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
