from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GetUserQuery:
    user_id: int


@dataclass(frozen=True)
class GetUserByUsernameQuery:
    username: str


@dataclass(frozen=True)
class GetUserByEmailQuery:
    email: str


@dataclass(frozen=True)
class ValidateTokenQuery:
    token: str


@dataclass(frozen=True)
class GetRefreshTokenQuery:
    jti: str


__all__ = [
    "GetUserQuery",
    "GetUserByUsernameQuery",
    "GetUserByEmailQuery",
    "ValidateTokenQuery",
    "GetRefreshTokenQuery",
]
