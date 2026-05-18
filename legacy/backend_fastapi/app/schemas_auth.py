from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# Схемы запросов/ответов для аутентификации и регистрации.


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    phone: str | None = None
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None


class LoginResponse(BaseModel):
    user: UserOut
    access_token: str
    refresh_token: str
    expires_in: int


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    refresh_token: str


class RegisterIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=60)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=4)
    full_name: str = Field(..., max_length=200)
    phone: str | None = None
    role: Literal["manager", "picker", "driver"] = "picker"
