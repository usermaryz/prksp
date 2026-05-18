"""
Auth Service — аутентификация, JWT access/refresh, таблица refresh_tokens.
"""
from __future__ import annotations

import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

SERVICE_NAME = "auth-service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "auth.db")
_raw_db = os.getenv("DATABASE_URL", "").strip()
if _raw_db:
    DATABASE_URL = _raw_db.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
else:
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
SECRET_KEY = os.getenv("SECRET_KEY", "wms-auth-service-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "internal-service-key-2024")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    role = Column(String(20), default="worker")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


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


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def create_access_token(user: User) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token_record(db: Session, user: User) -> str:
    """Создаёт запись в refresh_tokens и возвращает JWT refresh."""
    jti = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(user_id=user.id, token=jti, expires_at=expires_at))
    db.flush()
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "jti": jti,
        "exp": expires_at,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_internal_key(x_internal_key: str = Header(None)):
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal API key")
    return True


def _user_from_bearer(authorization: str | None, db: Session, token_type: str = "access") -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload or payload.get("type") != token_type:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload.get("sub", 0))).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def init_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        demo_users = [
            ("admin", "admin@wms.local", "admin", "Администратор", "admin"),
            ("manager", "manager@wms.local", "manager", "Менеджер", "manager"),
            ("picker", "picker@wms.local", "picker", "Сборщик", "picker"),
            ("driver", "driver@wms.local", "driver", "Водитель", "driver"),
        ]
        for username, email, password, full_name, role in demo_users:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                db.add(
                    User(
                        username=username,
                        email=email,
                        password_hash=hash_password(password),
                        full_name=full_name,
                        role=role,
                    )
                )
            else:
                user.password_hash = hash_password(password)
                user.role = role
                user.is_active = True
        db.commit()
        print(f"[{SERVICE_NAME}] Demo: admin/admin, manager/manager, picker/picker, driver/driver")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    print(f"[{SERVICE_NAME}] Starting on port {SERVICE_PORT}...")
    yield
    print(f"[{SERVICE_NAME}] Shutting down...")


app = FastAPI(title="Auth Service", version="1.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME, "port": SERVICE_PORT}


@app.post("/auth/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь заблокирован")

    user.last_login_at = datetime.utcnow()
    access_token = create_access_token(user)
    refresh_token = create_refresh_token_record(db, user)
    db.commit()

    return LoginResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.post("/auth/refresh", response_model=LoginResponse)
def refresh_tokens(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Неверный refresh-токен")

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=401, detail="Неверный refresh-токен")

    row = db.query(RefreshToken).filter(RefreshToken.token == jti).first()
    if not row or row.revoked_at is not None or row.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh-токен отозван или просрочен")

    user = db.query(User).filter(User.id == row.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    row.revoked_at = datetime.utcnow()
    access_token = create_access_token(user)
    new_refresh = create_refresh_token_record(db, user)
    db.commit()

    return LoginResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=new_refresh,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.post("/auth/logout")
def logout(body: LogoutRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if payload and payload.get("type") == "refresh":
        jti = payload.get("jti")
        if jti:
            row = db.query(RefreshToken).filter(RefreshToken.token == jti).first()
            if row and row.revoked_at is None:
                row.revoked_at = datetime.utcnow()
                db.commit()
    return {"status": "ok"}


@app.post("/auth/register", response_model=UserResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@app.get("/auth/me", response_model=UserResponse)
def get_me(authorization: str = Header(None), db: Session = Depends(get_db)):
    user = _user_from_bearer(authorization, db, token_type="access")
    return UserResponse.model_validate(user)


@app.post("/internal/validate", response_model=TokenValidationResponse)
def validate_token(
    authorization: str = Header(None),
    _: bool = Depends(verify_internal_key),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        return TokenValidationResponse(valid=False)
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return TokenValidationResponse(valid=False)
    user = db.query(User).filter(User.id == int(payload.get("sub", 0))).first()
    if not user or not user.is_active:
        return TokenValidationResponse(valid=False)
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
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
