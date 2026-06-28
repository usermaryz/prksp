from __future__ import annotations

from typing import Optional

from jose import JWTError, jwt


def decode_token(token: str, secret_key: str, algorithm: str) -> Optional[dict]:
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        return None
